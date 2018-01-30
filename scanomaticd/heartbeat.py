import logging
from collections import namedtuple

from .apigateway import APIError

LOG = logging.getLogger(__name__)


class HeartbeatCommand:

    def __init__(self, apigateway):
        self._apigateway = apigateway

    def __call__(self, daemon):
        try:
            self._apigateway.update_status(
                job=daemon.get_scanning_job(),
                next_scheduled_scan=daemon.get_next_scheduled_scan(),
            )
        except APIError as error:
            LOG.warning(
                "Unexpected response %s when posting status update",
                str(error)
            )
