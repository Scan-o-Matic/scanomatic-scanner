import pytest
import mock
from scanomaticd.client import Client
from scanomaticd.scannercontroller import ScannerError


def test_post_update_raises_wo_uuid():
    client = Client("localhost.com", ("saccharon", "mykes"))
    with pytest.raises(ScannerError):
        client.post_update("mitosis")


@mock.patch("scanomaticd.client.requests")
def test_post_update(mockuest):
    client = Client("localhost.com", ("saccharon", "mykes"))
    client.set_uuid("beer")
    client.post_update("mitosis")
    mockuest.post.assert_called_once()
