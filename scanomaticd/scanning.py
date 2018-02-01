from collections import namedtuple
from datetime import datetime
from hashlib import sha256
from io import BytesIO

from PIL import Image


ScanningJob = namedtuple('ScanningJob', ['id', 'interval', 'end_time'])

Scan = namedtuple('Scan', [
    'data', 'start_time', 'end_time', 'job_id', 'digest'
])


class ScanCommand:
    def __init__(self, scanner, scanstore, compress=True):
        self._scanner = scanner
        self._scanstore = scanstore
        self._compress = compress

    def __call__(self, job):
        start_time = datetime.now()
        data = self._scanner.scan()
        end_time = datetime.now()
        with Image.open(BytesIO(data)) as image:
            if self._compress:
                image_file = BytesIO()
                image.save(image_file, format="TIFF", compression='tiff_lzw')
                image_file.seek(0)
                data = image_file.read()
            scan = Scan(
                data=data,
                job_id=job.id,
                start_time=start_time,
                end_time=end_time,
                digest='sha256:{}'.format(
                    sha256(image.tobytes()).hexdigest()
                ),
            )
        self._scanstore.put(scan)
