import pytest
from unittest.mock import MagicMock
from http import HTTPStatus

from scanomaticd.heartbeat import HeartbeatCommand
from scanomaticd.apigateway import APIError


class TestScannerHeartbeat:

    def test_heartbeat_good_response(self):
        apigateway = MagicMock()
        daemon = MagicMock()
        daemon.get_scanning_job.return_value = None
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        assert apigateway.update_status.called_once()

    def test_heartbeat_bad_response(self):
        apigateway = MagicMock()
        apigateway.update_status.side_effect = APIError("")
        daemon = MagicMock()
        daemon.get_scanning_job.return_value = None
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        assert apigateway.update_status.called_once()
