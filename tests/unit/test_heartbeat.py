import mock
from scanomaticd.heartbeat import HeartbeatCommand


@mock.patch("scanomaticd.client.Client")
def test_heartbeat_execute(mocklient):
    heartbeat = HeartbeatCommand("dummyjob", mocklient)
    heartbeat.execute()
    mocklient.post_status.assert_called_once()
