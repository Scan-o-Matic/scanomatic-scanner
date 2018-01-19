from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import pytest
import responses

from scanomaticd.apigateway import APIGateway, APIError
from scanomaticd.scanning import ScanningJob


@pytest.fixture
def apigateway():
    return APIGateway('http://example.com/api')


class TestGetScannerJob:
    SCANNERID = 'sc4nn3r'
    URI = 'http://example.com/api/scanners/{}/job'.format(SCANNERID)

    @responses.activate
    def test_with_job(self, apigateway):
        responses.add(
            responses.GET, self.URI, json={
                'identifier': 'j0b',
                'start': '1985-10-26T01:20:00Z',
                'duration': 240,
                'interval': 60,
            },
        )
        job = apigateway.get_scanner_job(self.SCANNERID)
        assert job == ScanningJob(
            id='j0b',
            interval=timedelta(minutes=1),
            end_time=datetime(1985, 10, 26, 1, 24, tzinfo=timezone.utc),
        )

    @responses.activate
    def test_with_no_job(self, apigateway):
        responses.add(
            responses.GET, self.URI, body='null',
        )
        job = apigateway.get_scanner_job(self.SCANNERID)
        assert job is None

    @responses.activate
    def test_with_error(self, apigateway):
        responses.add(
            responses.GET,
            self.URI,
            status=HTTPStatus.INTERNAL_SERVER_ERROR,
        )
        with pytest.raises(APIError, match='Internal Server Error'):
            apigateway.get_scanner_job(self.SCANNERID)
