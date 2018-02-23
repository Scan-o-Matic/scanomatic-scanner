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
    def __init__(self, scanner, scanstore):
        self._scanner = scanner
        self._scanstore = scanstore

    def __call__(self, job):
        start_time = datetime.now()
        data = self._scanner.scan()
        end_time = datetime.now()
        with Image.open(BytesIO(data)) as image:
            data = self._compress_image(image)
        scan = Scan(
            data=data,
            job_id=job.id,
            start_time=start_time,
            end_time=end_time,
            digest='sha256:{}'.format(sha256(data).hexdigest()),
        )
        self._scanstore.put(scan)

    def _compress_image(self, image):
        image_file = BytesIO()
        image.save(image_file, format="TIFF", compression='tiff_adobe_deflate')
        image_file.seek(0)
        return image_file.read()
