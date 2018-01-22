import logging
from collections import namedtuple

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class HeartbeatCommand:
    def __init__(self, gateway):
        self._gateway = gateway

    def execute(self):
        LOG.debug("heartbeat")
        self._gateway.post_status("")
