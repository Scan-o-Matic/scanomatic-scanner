import logging
from http import HTTPStatus
from collections import namedtuple

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class HeartbeatCommand:
    OK_STATUS = {HTTPStatus.OK, HTTPStatus.CREATED}

    def __init__(self, apigateway):
        self._apigateway = apigateway

    def __call__(self, daemon):
        response_code = self._apigateway.update_status(
            job=daemon.get_scanning_job()
        )

        if response_code not in self.OK_STATUS:
            LOG.warning(
                "Unexpected response %s when posting status update",
                response_code
            )
