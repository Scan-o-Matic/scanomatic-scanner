import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
from http import HTTPStatus

from scanomaticd.heartbeat import HeartbeatCommand
from scanomaticd.apigateway import APIError


class TestScannerHeartbeat:

    @pytest.fixture
    def daemon(self):
        daemon = MagicMock()
        daemon.get_scanning_job.return_value = None
        daemon.get_next_scheduled_scan.return_value = None
        return daemon

    @pytest.fixture
    def apigateway(self):
        return MagicMock()

    @pytest.fixture
    def store(self):
        return ['Image 1', 'Image 55']

    @pytest.fixture
    def scanner(self):
        scanner = MagicMock()
        scanner.get_devices.return_value = ['epson']
        return scanner

    def test_heartbeat_good_response(self, daemon, apigateway, store, scanner):
        now = datetime.now(tz=timezone.utc)
        heartbeat = HeartbeatCommand(apigateway, store, scanner)
        daemon.get_start_time.return_value = now
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=None,
            next_scheduled_scan=None,
            images_to_send=2,
            start_time=now,
            devices=['epson'],
        )

    def test_heartbeat_bad_response_doesnt_raise(
            self, daemon, apigateway, store, scanner):
        apigateway.update_status.side_effect = APIError("")
        heartbeat = HeartbeatCommand(apigateway, store, scanner)
        heartbeat(daemon)

    def test_heartbeat_with_scheduled_scan(
            self, daemon, apigateway, store, scanner):
        now = datetime.now(tz=timezone.utc)
        scheduled = now + timedelta(minutes=20)
        daemon.get_next_scheduled_scan.return_value = scheduled
        daemon.get_start_time.return_value = now
        heartbeat = HeartbeatCommand(apigateway, store, scanner)
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=None,
            next_scheduled_scan=scheduled,
            images_to_send=2,
            start_time=now,
            devices=['epson'],
        )

    def test_heartbeat_with_job(
            self, daemon, apigateway, scanningjob, store, scanner):
        daemon.get_scanning_job.return_value = scanningjob
        now = datetime.now(tz=timezone.utc)
        daemon.get_start_time.return_value = now
        heartbeat = HeartbeatCommand(apigateway, store, scanner)
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=scanningjob.id,
            next_scheduled_scan=None,
            images_to_send=2,
            start_time=now,
            devices=['epson'],
        )

    def test_hearbeat_with_no_images_to_send(
            self, daemon, apigateway, scanningjob, store, scanner):
        daemon.get_scanning_job.return_value = scanningjob
        now = datetime.now(tz=timezone.utc)
        daemon.get_start_time.return_value = now
        heartbeat = HeartbeatCommand(apigateway, store, scanner)
        store.clear()
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=scanningjob.id,
            next_scheduled_scan=None,
            images_to_send=0,
            start_time=now,
            devices=['epson'],
        )
