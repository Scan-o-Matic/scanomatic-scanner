import logging
from collections import namedtuple

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


class HeartbeatCommand:
    OK_STATUS = {HTTPStatus.OK, HTTPStatus.CREATED}

    def __init__(self, apigateway):
        self._apigateway = apigateway

    def __call__(self, daemon):
        try:
            response_code = self._apigateway.update_status(
                job=daemon.get_scanning_job()
            )
        except APIError as error:
            LOG.warning(
                "Unexpected response %s when posting status update",
                error
            )
