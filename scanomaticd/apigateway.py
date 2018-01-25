from datetime import datetime, timedelta, timezone

import requests

from scanomaticd.scanning import ScanningJob


DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'


class APIError(Exception):
    pass


class APIGateway:
    def __init__(self, apibase, scannerid, username, password):
        self.apibase = apibase
        self.scannerid = scannerid
        self.username = username
        self.password = password

    def get_scanner_job(self):
        response = requests.get(
            self.apibase + '/scanners/{}/job'.format(self.scannerid),
            auth=(self.username, self.password),
        )
        try:
            response.raise_for_status()
        except requests.RequestException as error:
            raise APIError(str(error))
        data = response.json()
        if data is None:
            return
        start = _parse_datetime(data['startTime'])
        duration = timedelta(seconds=data['duration'])
        end = start + duration
        return ScanningJob(
            id=data['identifier'],
            interval=timedelta(seconds=data['interval']),
            end_time=end,
        )

    def post_scan(self, scan):
        response = requests.post(
            self.apibase + '/scans',
            auth=(self.username, self.password),
            data={
                'jobId': scan.job_id,
                'startTime': scan.start_time.strftime(DATETIME_FORMAT),
                'endTime': scan.end_time.strftime(DATETIME_FORMAT),
                'digest': scan.digest,
                'scannerId': self.scannerid,
            },
            files={'image': scan.data},
        )
        try:
            response.raise_for_status()
        except requests.RequestException as error:
            raise APIError(str(error))


def _parse_datetime(s):
    naive = datetime.strptime(s, DATETIME_FORMAT)
    return naive.replace(tzinfo=timezone.utc)
