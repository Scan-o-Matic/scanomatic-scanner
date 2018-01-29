from datetime import datetime, timedelta, timezone
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


class TestSetScanningJob:
    def test_remember_set_job(self, daemon, job):
        daemon.set_scanning_job(job)
        assert daemon.get_scanning_job() == job

    @pytest.mark.slow
    def test_complete_scanning_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(7)
        assert fakescancommand.calls == [
            (0, call(job)),
            (2, call(job)),
            (4, call(job)),
        ]

    @pytest.mark.slow
    def test_replace_existing_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(1)
        job2 = ScanningJob(
            id='1235',
            interval=timedelta(seconds=4),
            end_time=datetime.now() + timedelta(seconds=5),
        )
        daemon.set_scanning_job(job2)
        sleep(5)
        assert fakescancommand.calls == [
            (0, call(job)),
            (1, call(job2)),
            (5, call(job2)),
        ]

    @pytest.mark.slow
    def test_cancel_existing_job(self, daemon, job, fakescancommand):
        daemon.set_scanning_job(job)
        sleep(1)
        daemon.set_scanning_job(None)
        sleep(2)
        assert fakescancommand.calls == [
            (0, call(job)),
        ]

    def test_get_next_scheduled_scan_when_no_job(self, daemon):
        assert daemon.get_next_scheduled_scan() is None

    @pytest.mark.slow
    def test_get_next_scheduled_scan(self, daemon):
        now = datetime.now(timezone.utc)
        delta = timedelta(seconds=1200)
        job = ScanningJob(
            id='53412',
            interval=delta,
            end_time=now + 2 * delta
        )
        daemon.set_scanning_job(job)
        sleep(1)
        assert (
            (daemon.get_next_scheduled_scan() - (now + delta)).total_seconds()
            < 1
        )

    @pytest.mark.slow
    def test_get_next_scheduled_scan_when_job_canceled(self, daemon, job):
        daemon.set_scanning_job(job)
        sleep(1)
        daemon.set_scanning_job(None)
        sleep(2)
        assert daemon.get_next_scheduled_scan() is None


@pytest.mark.slow
class TestUpdateCommand:
    def test_run_every_minutes(self, daemon, fakeupdatecommand):
        sleep(120)
        assert fakeupdatecommand.calls == [
            (0, call(daemon)),
            (60, call(daemon)),
            (120, call(daemon)),
        ]
