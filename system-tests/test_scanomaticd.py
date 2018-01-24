from datetime import datetime, timedelta
from glob import glob
import time
import uuid
import os

import docker
import pytest
import requests

SCANDURATION = timedelta(minutes=3)
APIROOT = 'https://som.molflow.com/api'
APIROOT = 'http://192.168.74.130:5050/api'
USERNAME = os.environ['SCANOMATIC_USERNAME']
PASSWORD = os.environ['SCANOMATIC_PASSWORD']


@pytest.fixture
def scannerid():
    return '9a8486a6f9cb11e7ac660050b68338ac'


@pytest.fixture(autouse=True)
def scanning_job(scannerid):
    response = requests.post(
        APIROOT + '/scan-jobs',
        json={
            'name': uuid.uuid1().hex, 'interval': 300, 'duration': 660,
            'scannerId': scannerid,
        },
        auth=(USERNAME, PASSWORD),
    )
    print(response.json())
    response.raise_for_status()
    jobid = response.json()['jobId']
    (requests
        .post(APIROOT + '/scan-jobs/{}/start'.format(jobid))
        .raise_for_status())


@pytest.fixture(autouse=True)
def scanomaticd(tmpdir, scannerid):
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
            tmpdir: {'bind': '/var/scanomaticd', 'mode': 'rw'},
            '/dev/bus/usb': {'bind': '/dev/bus/usb', 'mode': 'rw'},
        },
    )
    yield container
    container.stop()
    print(container.logs().decode('utf-8'))
    container.remove()


def test(tmpdir, scanomaticd):
    nbscans = 3
    interval = timedelta(minutes=5)
    begin = datetime.now()
    scantimes = []
    while datetime.now() - begin < (nbscans + 1) * interval:
        if len(glob(str(tmpdir.join('scans', '*.tiff')))) > len(scantimes):
            scantimes.append(datetime.now())
        assert scanomaticd.status in {'created', 'running'}
        time.sleep(1)
    assert len(scantimes) == nbscans
    assert scantimes[0] - begin < SCANDURATION
    assert interval < scantimes[1] - begin < interval + SCANDURATION
    assert 2 * interval < scantimes[2] - begin < 2 * interval + SCANDURATION
