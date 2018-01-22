import mock
from scanomaticd.heartbeat import HeartbeatCommand


@mock.patch("scanomaticd.gateway.Gateway")
def test_heartbeat_execute(mockway):
    heartbeat = HeartbeatCommand(mockway)
    heartbeat.execute()
    mockway.post_status.assert_called_once()
