from base64 import b64encode
from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest
import responses

from scanomaticd.apigateway import APIGateway, APIError
from scanomaticd.scanning import ScanningJob


SCANNERID = 'sc4nn3r'


@pytest.fixture
def apigateway():
    return APIGateway(
        'http://example.com/api',
        SCANNERID,
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
    URI = 'http://example.com/api/scanners/{}/job'.format(SCANNERID)

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
    URI = 'http://example.com/api/scanners/{}/status'.format(SCANNERID)

    @responses.activate
    def test_update_status_registered_scanner(self, apigateway):
        responses.add(responses.PUT, self.URI, body='null')
        response_code = apigateway.update_status("")
        assert response_code == 200
