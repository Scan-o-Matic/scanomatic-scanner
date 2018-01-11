from collections import namedtuple
from datetime import datetime
from hashlib import sha256


ScanningJob = namedtuple('ScanningJob', ['id', 'interval', 'end_time'])

Scan = namedtuple('Scan', [
    'data', 'start_time', 'end_time', 'job_id', 'digest'
])


class ScanCommand:
    def __init__(self, job, scanner, scanstore):
        self._job = job
        self._scanner = scanner
        self._scanstore = scanstore

    def execute(self):
        start_time = datetime.now()
        data = self._scanner.scan()
        end_time = datetime.now()
        scan = Scan(
            data=data,
            job_id=self._job.id,
            start_time=start_time,
            end_time=end_time,
            digest='sha256:{}'.format(sha256(data).hexdigest()),
        )
        self._scanstore.put(scan)
