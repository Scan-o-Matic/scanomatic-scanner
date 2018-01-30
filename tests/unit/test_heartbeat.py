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

    def test_heartbeat_good_response(self, daemon, apigateway):
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=None, next_scheduled_scan=None,
        )

    def test_heartbeat_bad_response_doesnt_raise(self, daemon, apigateway):
        apigateway.update_status.side_effect = APIError("")
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)

    def test_heartbeat_with_scheduled_scan(self, daemon, apigateway):
        now = datetime.now(tz=timezone.utc)
        scheduled = now + timedelta(minutes=20)
        daemon.get_next_scheduled_scan.return_value = scheduled
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=None, next_scheduled_scan=scheduled,
        )

    def test_heartbeat_with_job(self, daemon, apigateway, scanningjob):
        daemon.get_scanning_job.return_value = scanningjob
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        apigateway.update_status.assert_called_once_with(
            job=scanningjob.id, next_scheduled_scan=None,
        )
