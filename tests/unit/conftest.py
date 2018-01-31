from datetime import datetime, timedelta

import pytest

from scanomaticd.scanning import ScanningJob


@pytest.fixture
def scanningjob():
    return ScanningJob(
        id='abcd',
        interval=timedelta(minutes=3),
        end_time=datetime(1985, 10, 26, 1, 35)
    )
