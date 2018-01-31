import logging
from collections import namedtuple

from .apigateway import APIError

LOG = logging.getLogger(__name__)


class HeartbeatCommand:

    def __init__(self, apigateway, store):
        self._apigateway = apigateway
        self._store = store

    def __call__(self, daemon):
        currentjob = daemon.get_scanning_job()
        try:
            self._apigateway.update_status(
                job=currentjob.id if currentjob else None,
                next_scheduled_scan=daemon.get_next_scheduled_scan(),
                images_to_send=len(self._store),
                uptime=daemon.get_uptime().total_seconds(),
            )
        except APIError as error:
            LOG.warning(
                "Unexpected response %s when posting status update",
                str(error)
            )
