from datetime import datetime, timedelta, timezone
from glob import glob
try:
    from http import HTTPStatus
except ImportError:
    import http.client as HTTPStatus
import time
import uuid
import os

import docker
import pytest
from requests import Session

APIROOT = 'https://som.molflow.com/api'
USERNAME = os.environ['SCANOMATIC_USERNAME']
PASSWORD = os.environ['SCANOMATIC_PASSWORD']


@pytest.fixture
def scannerid():
    return 'test-scanner:{}'.format(uuid.uuid4())


@pytest.fixture
def scanomaticd(scannerid):
    dockerclient = docker.from_env()
    container = dockerclient.containers.run(
        'scanomaticd:latest',
        detach=True,
        environment={
            'SCANOMATICD_APIROOT': APIROOT,
            'SCANOMATICD_APIUSERNAME': USERNAME,
            'SCANOMATICD_APIPASSWORD': PASSWORD,
            'SCANOMATICD_SCANNERID': scannerid,
        },
        privileged=True,
        volumes={
            '/dev/bus/usb': {'bind': '/dev/bus/usb', 'mode': 'rw'},
        },
    )
    yield container
    container.stop()
    print(container.logs().decode('utf-8'))
    container.remove()


class ScanomaticGateway:
    def __init__(self):
        self._session = Session()
        self._session.auth = (USERNAME, PASSWORD)

    def create_scan_job(self, scannerid, interval, duration):
        response = self._session.post(
            APIROOT + '/scan-jobs',
            json={
                'name': uuid.uuid1().hex,
                'interval': interval.total_seconds(),
                'duration': duration.total_seconds(),
                'scannerId': scannerid,
            },
        )
        response.raise_for_status()
        return response.json()['identifier']

    def start_scan_job(self, jobid):
        (self
            ._session.post(self.mkurl('/scan-jobs/{}/start', jobid))
            .raise_for_status())

    def has_scanner(self, scannerid):
        response = self._session.get(self.mkurl('/scanners/{}', scannerid))
        if response.status_code == HTTPStatus.NOT_FOUND:
            return False
        response.raise_for_status()
        return True

    def get_scan_times(self, jobid):
        response = self._session.get(self.mkurl('/scans'))
        response.raise_for_status()
        return [
            (datetime
                .strptime(obj['startTime'], '%Y-%m-%dT%H:%M:%SZ')
                .replace(tzinfo=timezone.utc))
            for obj in response.json() if obj['scanJobId'] == jobid
        ]

    def mkurl(self, pattern, *args):
        return APIROOT + pattern.format(*args)


@pytest.fixture
def scanomatic():
    return ScanomaticGateway()


def test(tmpdir, scanomaticd, scannerid, scanomatic):
    jitter = timedelta(minutes=1)  # time for the scanner to pick-up the job
    scaninterval = timedelta(minutes=5)
    duration = 2 * scaninterval + jitter

    # We need to wait until the scanner has sent its first status update
    waitbegin = datetime.now()
    while datetime.now() - waitbegin < timedelta(minutes=1):
        if scanomatic.has_scanner(scannerid):
            break
        time.sleep(1)
    else:
        pytest.fail('Timeout while waiting for the scanner to appear')

    scanjobid = scanomatic.create_scan_job(scannerid, scaninterval, duration)
    scanomatic.start_scan_job(scanjobid)
    begin = datetime.now(timezone.utc)

    # Waiting one more interval than necessary to make sure the scanning
    # properly terminates
    while datetime.now(timezone.utc) - begin < (3 * scaninterval + jitter):
        time.sleep(10)
        scanomaticd.reload()
        assert scanomaticd.status in {'running'}

    scantimes = scanomatic.get_scan_times(scanjobid)
    scantimes.sort()
    assert len(scantimes) == 3
    assert scantimes[0] - begin < jitter
    assert scantimes[1] - begin < scaninterval + jitter
    assert scantimes[2] - begin < 2 * scaninterval + jitter
