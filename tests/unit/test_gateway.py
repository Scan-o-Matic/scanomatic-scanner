import pytest
import mock
from scanomaticd.gateway import Gateway
from scanomaticd.scannercontroller import ScannerError


def test_post_update_raises_wo_uuid():
    gateway = Gateway("localhost.com", ("saccharon", "mykes"))
    with pytest.raises(ScannerError):
        gateway.post_update("mitosis")


@mock.patch("scanomaticd.gateway.requests")
def test_post_update(mockuest):
    gateway = Gateway("localhost.com", ("saccharon", "mykes"))
    gateway.set_uuid("beer")
    gateway.post_update("mitosis")
    mockuest.post.assert_called_once()
