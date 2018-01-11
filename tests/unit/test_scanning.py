from datetime import datetime, timedelta
from hashlib import sha256
from unittest.mock import MagicMock

from freezegun import freeze_time
import pytest

from scanomaticd.scanning import ScanCommand, Scan, ScanningJob


@pytest.fixture
def scanningjob():
    return ScanningJob(
        id='abcd',
        interval=timedelta(minutes=3),
        end_time=datetime(1985, 10, 26, 1, 35)
    )


class FakeScanner:
    def __init__(self, data, frozen_time):
        self.data = data
        self.time = frozen_time

    def scan(self):
        self.time.tick(delta=timedelta(minutes=1))
        return self.data


def test_scancommand(scanningjob):
    now = datetime(1985, 10, 26, 1, 20)
    fakedata = b'I am a scan'
    scanstore = MagicMock()
    with freeze_time(now) as faketime:
        scanner = FakeScanner(fakedata, faketime)
        scancommand = ScanCommand(scanningjob, scanner, scanstore)
        scancommand.execute()
    scanstore.put.assert_called_with(
        Scan(
            data=fakedata,
            job_id='abcd',
            start_time=now,
            end_time=now + timedelta(minutes=1),
            digest='sha256:{}'.format(sha256(fakedata).hexdigest()),
        ),
    )
