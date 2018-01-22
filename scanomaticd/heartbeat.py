import logging
from collections import namedtuple

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


HeartbeatJob = namedtuple('HeartbeatJob', ['id', 'interval'])


class HeartbeatCommand:
    def __init__(self, job, client):
        self._job = job
        self._client = client

    def execute(self):
        LOG.debug("heartbeat")
        self._client.post_status("")
