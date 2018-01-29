import logging
from collections import namedtuple

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class HeartbeatCommand:
    def __init__(self, apigateway):
        self._apigateway = apigateway

    def __call__(self, daemon):
        LOG.debug("heartbeat")

        response_code = self._apigateway.update_status(
            job=daemon.get_scanning_job()
        )

        if response_code != 200:
            LOG.warning(
                "Unexpected response %s when posting status update",
                response_code
            )
