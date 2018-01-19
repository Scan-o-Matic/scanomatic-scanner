from datetime import datetime, timedelta, timezone

import requests

from scanomaticd.scanning import ScanningJob


class APIError(Exception):
    pass


class APIGateway:
    def __init__(self, apibase):
        self.apibase = apibase

    def get_scanner_job(self, scannerid):
        response = requests.get(
            self.apibase + '/scanners/sc4nn3r/job'
        )
        try:
            response.raise_for_status()
        except requests.RequestException as error:
            raise APIError(str(error))
        data = response.json()
        if data is None:
            return
        start = _parse_datetime(data['start'])
        duration = timedelta(seconds=data['duration'])
        end = start + duration
        return ScanningJob(
            id=data['identifier'],
            interval=timedelta(seconds=data['interval']),
            end_time=end,
        )


def _parse_datetime(s):
    naive = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return naive.replace(tzinfo=timezone.utc)
