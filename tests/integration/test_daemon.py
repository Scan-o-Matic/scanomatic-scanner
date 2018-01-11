from datetime import datetime, timedelta
import time

import pytest

from scanomaticd.scanning import ScanningJob
from scanomaticd.daemon import ScanDaemon
from scanomaticd.scannercontroller import ScanimageScannerController
from scanomaticd.scanstore import ScanStore


def wait(**kwargs):
    time.sleep(timedelta(**kwargs).total_seconds())


@pytest.fixture
def store(tmpdir):
    return ScanStore(str(tmpdir))


@pytest.fixture
def daemon(store):
    scanner = ScanimageScannerController()
    job = ScanningJob(
        id='abcd',
        interval=timedelta(minutes=5),
        end_time=datetime.now() + timedelta(minutes=20),
    )
    return ScanDaemon(scanner, store, job)


## def test_daemon(store, daemon):
##     daemon.start()
##     wait(minutes=30)
##     assert len(store) == 4
