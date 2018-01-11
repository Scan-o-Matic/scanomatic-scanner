from datetime import datetime, timedelta
from time import sleep
from unittest.mock import MagicMock

from apscheduler.schedulers.background import BackgroundScheduler
import pytest

from scanomaticd.daemon import ScanDaemon
from scanomaticd.scanning import ScanningJob


@pytest.fixture
def fakescancommand():
    return MagicMock()


@pytest.fixture
def daemon(fakescancommand):
    job = ScanningJob(
        id='1234',
        interval=timedelta(seconds=2),
        end_time=datetime.now() + timedelta(seconds=5),
    )
    daemon = ScanDaemon(job, fakescancommand, scheduler=BackgroundScheduler)
    yield daemon
    daemon.stop()


def test_scandaemon_scans_on_start(daemon, fakescancommand):
    assert fakescancommand.execute.call_count == 0
    daemon.start()
    assert fakescancommand.execute.call_count == 1


def test_scandaemon_scans_every_interval(daemon, fakescancommand):
    daemon.start()
    sleep(2)
    assert fakescancommand.execute.call_count == 2
    sleep(2)
    assert fakescancommand.execute.call_count == 3


def test_scandaemon_stops_after_endtime(daemon, fakescancommand):
    daemon.start()
    sleep(8)
    assert fakescancommand.execute.call_count == 3
