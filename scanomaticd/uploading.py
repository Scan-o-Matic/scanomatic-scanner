from collections import namedtuple
from datetime import datetime
import logging

from .apigateway import APIError

LOG = logging.getLogger(__name__)


class UploadCommand:
    def __init__(self, apigateway, scanstore):
        self._apigateway = apigateway
        self._scanstore = scanstore

    def __call__(self):
        LOG.info('%d scans to upload', len(self._scanstore))
        for scan in self._scanstore:
            self._apigateway.post_scan(scan)
            self._scanstore.delete(scan)
