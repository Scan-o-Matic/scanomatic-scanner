class UpdateScanningJobCommand:
    def __init__(self, scannerid, apigateway):
        self._scannerid = scannerid
        self._apigateway = apigateway

    def __call__(self, daemon, currentjob):
        newjob = self._apigateway.get_scanner_job(self._scannerid)
        if newjob != currentjob:
            daemon.set_scanjob(newjob)
