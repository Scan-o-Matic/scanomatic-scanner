from datetime import datetime, timezone
from hashlib import sha256

import pytest
from unittest.mock import MagicMock, call

from scanomaticd.apigateway import APIError
from scanomaticd.uploading import UploadCommand
from scanomaticd.scanning import Scan


@pytest.fixture
def scans():
    fakedata = b'foobar'
    return [
        Scan(
            data=fakedata,
            job_id='abcd',
            start_time=datetime(1985, 10, 26, 1, 20, tzinfo=timezone.utc),
            end_time=datetime(1985, 10, 26, 1, 21, tzinfo=timezone.utc),
            digest='sha256:{}'.format(sha256(fakedata).hexdigest()),
        ),
        Scan(
            data=fakedata,
            job_id='abcd',
            start_time=datetime(1985, 10, 26, 1, 30, tzinfo=timezone.utc),
            end_time=datetime(1985, 10, 26, 1, 31, tzinfo=timezone.utc),
            digest='sha256:{}'.format(sha256(fakedata).hexdigest()),
        ),
    ]


class TestUploadCommand:
    def test_do_nothing_if_no_scans(self):
        apigateway = MagicMock()
        scanstore = MagicMock()
        command = UploadCommand(apigateway, scanstore)
        command()
        apigateway.post_scan.assert_not_called()

    def test_upload_scans(self, scans):
        apigateway = MagicMock()
        scanstore = MagicMock()
        scanstore.__iter__.return_value = scans
        command = UploadCommand(apigateway, scanstore)
        command()
        apigateway.post_scan.assert_has_calls([call(scan) for scan in scans])

    def test_delete_the_scans_on_success(self, scans):
        apigateway = MagicMock()
        scanstore = MagicMock()
        scanstore.__iter__.return_value = scans
        command = UploadCommand(apigateway, scanstore)
        command()
        scanstore.delete.assert_has_calls([call(scan) for scan in scans])

    def test_doesnt_delete_the_scan_on_error(self, scans):
        apigateway = MagicMock()
        apigateway.post_scan.side_effect = APIError
        scanstore = MagicMock()
        scanstore.__iter__.return_value = scans
        command = UploadCommand(apigateway, scanstore)
        with pytest.raises(APIError):
            command()
        scanstore.delete.assert_not_called()
