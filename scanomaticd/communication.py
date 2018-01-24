import logging


LOG = logging.getLogger(__name__)


class UpdateScanningJobCommand:
    def __init__(self, apigateway):
        self._apigateway = apigateway

    def __call__(self, daemon):
        currentjob = daemon.get_scanning_job()
        newjob = self._apigateway.get_scanner_job()
        if newjob != currentjob:
            LOG.info('New job: {}'.format(newjob))
            daemon.set_scanning_job(newjob)
