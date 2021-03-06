from base64 import b64encode
from datetime import datetime, timedelta, timezone
import email
from http import HTTPStatus

import json
import pytest
import responses

from scanomaticd.scanning import Scan
from scanomaticd.apigateway import APIGateway, APIError
from scanomaticd.scanning import ScanningJob


SCANNER_ID = 'sc4nn3r'


@pytest.fixture
def apigateway():
    return APIGateway(
        'http://example.com/api',
        SCANNER_ID,
        'myuser',
        'mypassword'
    )


def assert_authorized(request):
    assert 'Authorization' in request.headers
    assert (
        request.headers['Authorization']
        == 'Basic {}'.format(b64encode(b'myuser:mypassword').decode('ascii'))
    )


class TestGetScannerJob:
    URI = 'http://example.com/api/scanners/{}/job'.format(SCANNER_ID)

    @responses.activate
    def test_authorization(self, apigateway):
        responses.add(responses.GET, self.URI, body='null')
        apigateway.get_scanner_job()
        assert_authorized(responses.calls[0].request)

    @responses.activate
    def test_return_job(self, apigateway):
        responses.add(
            responses.GET, self.URI, json={
                'identifier': 'j0b',
                'startTime': '1985-10-26T01:20:00Z',
                'duration': 240,
                'interval': 60,
            },
        )
        job = apigateway.get_scanner_job()
        assert job == ScanningJob(
            id='j0b',
            interval=timedelta(minutes=1),
            end_time=datetime(1985, 10, 26, 1, 24, tzinfo=timezone.utc),
        )

    @responses.activate
    def test_return_none_if_no_job(self, apigateway):
        responses.add(responses.GET, self.URI, body='null')
        job = apigateway.get_scanner_job()
        assert job is None

    @responses.activate
    def test_with_error(self, apigateway):
        responses.add(
            responses.GET,
            self.URI,
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        with pytest.raises(APIError, match='Internal Server Error'):
            apigateway.get_scanner_job()


class TestUpdateScannerStatus:
    URI = 'http://example.com/api/scanners/{}/status'.format(SCANNER_ID)

    @responses.activate
    @pytest.mark.parametrize(
        "response",
        [HTTPStatus.OK, HTTPStatus.CREATED]
    )
    def test_update_status_good_response_not_raises(
        self, apigateway, response
    ):
        responses.add(responses.PUT, self.URI, body='null', status=response)
        apigateway.update_status("")

    @responses.activate
    @pytest.mark.parametrize(
        "response",
        [HTTPStatus.GATEWAY_TIMEOUT, HTTPStatus.BAD_REQUEST]
    )
    def test_update_status_bad_response_raises(self, apigateway, response):
        responses.add(responses.PUT, self.URI, body='null', status=response)
        with pytest.raises(APIError):
            apigateway.update_status("")

    @responses.activate
    def test_update_status_posts_job(self, apigateway):
        responses.add(responses.PUT, self.URI, body='null')
        job = {'this': 'is a job'}
        apigateway.update_status(job=job)
        assert (
            json.loads(responses.calls[0].request.body.decode())['job'] == job
        )

    @responses.activate
    def test_update_status_posts_next_scheduled_scan(self, apigateway):
        responses.add(responses.PUT, self.URI, body='null')
        dt = datetime(1980, 3, 23, 13, 55, tzinfo=timezone.utc)
        apigateway.update_status(next_scheduled_scan=dt)
        assert (
            json.loads(
                responses.calls[0].request.body.decode()
            )['nextScheduledScan'] == '1980-03-23T13:55:00Z'
        )

    @responses.activate
    def test_update_status_posts_images_to_send(self, apigateway):
        responses.add(responses.PUT, self.URI, body='null')
        images_to_send = 42
        apigateway.update_status(images_to_send=images_to_send)
        assert (
            json.loads(
                responses.calls[0].request.body.decode()
            )['imagesToSend'] == images_to_send
        )

    @responses.activate
    def test_update_status_posts_uptime(self, apigateway):
        responses.add(responses.PUT, self.URI, body='null')
        dt = datetime(1980, 3, 23, 13, 55, tzinfo=timezone.utc)
        apigateway.update_status(start_time=dt)
        assert (
            json.loads(
                responses.calls[0].request.body.decode()
            )['startTime'] == '1980-03-23T13:55:00Z'
        )


class TestPostScan:
    URI = 'http://example.com/api/scans'

    @pytest.fixture
    def scan(self):
        return Scan(
            data=b'foobar',
            job_id='abcd',
            start_time=datetime(1985, 10, 26, 1, 20, tzinfo=timezone.utc),
            end_time=datetime(1985, 10, 26, 1, 21, tzinfo=timezone.utc),
            digest='foo:bar',
        )

    @responses.activate
    def test_url(self, scan, apigateway):
        responses.add(responses.POST, self.URI)
        apigateway.post_scan(scan)
        assert responses.calls[0].request.url == self.URI

    @responses.activate
    def test_authorization(self, scan, apigateway):
        responses.add(responses.POST, self.URI)
        apigateway.post_scan(scan)
        assert_authorized(responses.calls[0].request)

    @responses.activate
    def test_send_data(self, scan, apigateway):
        responses.add(responses.POST, self.URI)
        apigateway.post_scan(scan)
        assert b'foobar' in responses.calls[0].request.body

    @responses.activate
    def test_send_metadata(self, scan, apigateway):
        responses.add(responses.POST, self.URI)
        apigateway.post_scan(scan)
        data, files = parse_request(responses.calls[0].request)
        assert data == {
            'scanJobId': 'abcd',
            'startTime': '1985-10-26T01:20:00Z',
            'endTime': '1985-10-26T01:21:00Z',
            'digest': 'foo:bar',
        }

    @responses.activate
    def test_with_error(self, scan, apigateway):
        responses.add(
            responses.POST,
            self.URI,
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        with pytest.raises(APIError, match='Internal Server Error'):
            apigateway.post_scan(scan)


def parse_request(request):
    files = dict()
    data = dict()
    content = email.message_from_bytes(
        b'Content-Type: ' + request.headers['Content-Type'].encode('ascii')
        + b'\r\n\r\n' +
        responses.calls[0].request.body)
    for part in content.get_payload():
        name = part.get_param('name', None, 'Content-Disposition')
        if name is None:
            continue
        filename = part.get_filename()
        if filename is None:
            data[name] = part.get_payload()
        else:
            files[name] = (filename, part.get_payload())
    return data, files
