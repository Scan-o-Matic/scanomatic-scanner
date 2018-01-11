from datetime import datetime, timedelta
from glob import glob
import time

import docker
import pytest

SCANDURATION = timedelta(minutes=3)


@pytest.fixture(autouse=True)
def scanomaticd(tmpdir):
    dockerclient = docker.from_env()
    container = dockerclient.containers.run(
        'scanomaticd:latest',
        detach=True,
        privileged=True,
        volumes={
            tmpdir: {'bind': '/var/scanomaticd', 'mode': 'rw'},
            '/dev/bus/usb': {'bind': '/dev/bus/usb', 'mode': 'rw'},
        },
    )
    yield
    container.stop()
    print(container.logs().decode('utf-8'))
    container.remove()


def test(tmpdir):
    nbscans = 3
    interval = timedelta(minutes=5)
    begin = datetime.now()
    scantimes = []
    while datetime.now() - begin < (nbscans + 1) * interval:
        if len(glob(str(tmpdir.join('scans', '*.tiff')))) > len(scantimes):
            scantimes.append(datetime.now())
        time.sleep(1)
    assert len(scantimes) == nbscans
    assert scantimes[0] - begin < SCANDURATION
    assert interval < scantimes[1] - begin < interval + SCANDURATION
    assert 2 * interval < scantimes[2] - begin < 2 * interval + SCANDURATION
