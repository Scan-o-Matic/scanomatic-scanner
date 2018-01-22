from datetime import datetime, timedelta
from time import sleep
from unittest.mock import MagicMock, call

from apscheduler.schedulers.background import BackgroundScheduler
import pytest

from scanomaticd.daemon import ScanDaemon
from scanomaticd.scanning import ScanningJob


class FakeCommand:
    def __init__(self):
        self.start = datetime.now()
        self.calls = []

    def __call__(self, *args, **kwargs):
        delta = datetime.now() - self.start
        seconds = round(delta.total_seconds())
        self.calls.append((seconds, call(*args, **kwargs)))


@pytest.fixture
def fakescancommand():
    return FakeCommand()


@pytest.fixture
def fakeupdatecommand():
    return FakeCommand()


@pytest.fixture
def daemon(fakescancommand, fakeupdatecommand):
    daemon = ScanDaemon(
        fakeupdatecommand, fakescancommand, scheduler=BackgroundScheduler
    )
    daemon.start()
    yield daemon
    daemon.stop()


@pytest.fixture
def job():
    return ScanningJob(
        id='1234',
        interval=timedelta(seconds=2),
        end_time=datetime.now() + timedelta(seconds=5),
    )


@pytest.mark.slow
class TestSetScanningJob:
    def test_complete_scanning_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(7)
        assert fakescancommand.calls == [
            (0, call(job)),
            (2, call(job)),
            (4, call(job)),
        ]

    def test_replace_existing_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(1)
        job2 = ScanningJob(
            id='1235',
            interval=timedelta(seconds=4),
            end_time=datetime.now() + timedelta(seconds=5),
        )
        daemon.set_scanning_job(job2)
        sleep(4)
        assert fakescancommand.calls == [
            (0, call(job)),
            (1, call(job2)),
            (5, call(job2)),
        ]

    def test_cancel_existing_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(1)
        daemon.set_scanning_job(None)
        sleep(2)
        assert fakescancommand.calls == [
            (0, call(job)),
        ]


@pytest.mark.slow
class TestUpdateCommand:
    def test_run_every_minutes(self, daemon, fakeupdatecommand):
        sleep(120)
        assert fakeupdatecommand.calls == [
            (0, call(daemon, None)),
            (60, call(daemon, None)),
            (120, call(daemon, None)),
        ]
