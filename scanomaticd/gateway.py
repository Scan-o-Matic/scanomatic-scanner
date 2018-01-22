import requests
import logging
from .scannercontroller import ScannerError

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class Gateway:

    def __init__(self, host, auth):
        self._uuid = None
        self._host = host
        self._auth = auth

    def set_uuid(self, uuid):
        self._uuid = uuid

    def post_update(self, message=""):
        if self._uuid is None:
            raise ScannerError("Tried to post update before setting uuid.")

        url = "{host}/api/scanner/{uuid}/status".format(
            host=self._host, uuid=self._uuid)

        req = requests.post(url, json={"message": message}, auth=self._auth)

        if req.status != 200:
            LOG.warning(
                "Unexpected response {response} when posting to {url}".format(
                response=req.status, url=url)
            )
