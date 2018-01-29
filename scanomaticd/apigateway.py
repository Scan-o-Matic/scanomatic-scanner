from datetime import datetime, timedelta, timezone

import requests

from scanomaticd.scanning import ScanningJob


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

    def update_status(self, job=None):
        url = "{apibase}/scanners/{scannerid}/status".format(
            apibase=self.apibase, scannerid=self.scannerid)

        req = requests.put(
            url, json={"job": job}, auth=(self.username, self.password)
        )

        return req.status_code


def _parse_datetime(s):
    naive = datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ')
    return naive.replace(tzinfo=timezone.utc)
