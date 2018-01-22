from unittest.mock import MagicMock

import pytest

from scanomaticd.communication import UpdateScanningJobCommand


class TestUpdateScanningJobCommand:
    @pytest.fixture
    def job(self):
        return MagicMock()

    @pytest.fixture
    def command(self, job):
        apigateway = MagicMock()
        apigateway.get_scanner_job.return_value = job
        return UpdateScanningJobCommand('sc4nn3r', apigateway)

    def test_it_sets_scanjob(self, command, job):
        daemon = MagicMock()
        command(daemon, None)
        daemon.set_scanjob.assert_called_with(job)

    def test_doesnt_set_scanjob_if_not_changed(self, command, job):
        daemon = MagicMock()
        command(daemon, job)
        daemon.set_scanjob.assert_not_called()
