from datetime import datetime, timedelta
from hashlib import sha256
from unittest.mock import MagicMock
import pytest
from io import BytesIO

from freezegun import freeze_time
from PIL import Image

from scanomaticd.scanning import ScanCommand, Scan


class FakeScanner:
    def __init__(self, data, frozen_time):
        self.data = data
        self.time = frozen_time

    def scan(self):
        self.time.tick(delta=timedelta(minutes=1))
        return self.data


@pytest.fixture
def fake_data():
    fake = BytesIO()
    Image.new('L', (4, 2)).save(fake, 'TIFF')
    fake.seek(0)
    return fake.read()


def test_scancommand(scanningjob, fake_data):
    now = datetime(1985, 10, 26, 1, 20)
    scanstore = MagicMock()
    with freeze_time(now) as faketime:
        scanner = FakeScanner(fake_data, faketime)
        scancommand = ScanCommand(scanner, scanstore)
        scancommand(scanningjob)

    image = Image.open(BytesIO(fake_data))
    image_data = BytesIO()
    image.save(image_data, format='TIFF', compression="tiff_lzw")
    image_data.seek(0)

    scanstore.put.assert_called_with(
        Scan(
            data=image_data.read(),
            job_id=scanningjob.id,
            start_time=now,
            end_time=now + timedelta(minutes=1),
            digest='sha256:{}'.format(
                sha256(image.tobytes()).hexdigest()),
        ),
    )


def test_compression(fake_data):
    scancommand = ScanCommand(None, None)

    image_raw = Image.open(BytesIO(fake_data))
    comp_data = scancommand._compress_image(image_raw)
    image_cmp = Image.open(BytesIO(comp_data))

    assert image_raw.tobytes() == image_cmp.tobytes()
    assert fake_data != comp_data
