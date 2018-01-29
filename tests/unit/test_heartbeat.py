import pytest
from unittest.mock import MagicMock
from http import HTTPStatus

from scanomaticd.heartbeat import HeartbeatCommand


class TestScannerHeartbeat:

    @pytest.mark.parametrize("status", [HTTPStatus.OK, HTTPStatus.CREATED])
    def test_heartbeat_good(self, status):
        apigateway = MagicMock()
        apigateway.update_status.return_value = status
        daemon = MagicMock()
        daemon.get_scanning_job.return_value = None
        heartbeat = HeartbeatCommand(apigateway)
        heartbeat(daemon)
        assert apigateway.update_status.called_once()
