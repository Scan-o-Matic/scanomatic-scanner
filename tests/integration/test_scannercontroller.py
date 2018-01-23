from io import BytesIO

from PIL import Image
import pytest

from scanomaticd.scannercontroller import (
    ScanimageScannerController,
    ScannerError,
)


PIL_8BITS_BW_MODE = 'L'


class FakeScanimage:
    def __init__(self, monkeypatch, fixturesdir):
        self.path = fixturesdir.join('fakescanimage/bin')
        self.monkeypatch = monkeypatch

    def install(self):
        self.monkeypatch.setenv('PATH', self.path, prepend=':')

    def seterror(self, error):
        self.monkeypatch.setenv('FAKESCANIMAGE_ERROR', error)

    def setdevices(self, *devices):
        self.monkeypatch.setenv('FAKESCANIMAGE_DEVICES', ' '.join(devices))


@pytest.fixture
def fakescanimage(monkeypatch, fixturesdir):
    return FakeScanimage(monkeypatch, fixturesdir)


@pytest.fixture
def usbscanner(request, monkeypatch, fixturesdir):
    if not request.config.getoption("--with-scanner"):
        fakescanimage = FakeScanimage(monkeypatch, fixturesdir)
        fakescanimage.install()


class TestScanimageScannerController:

    def test_init(self, fakescanimage):
        fakescanimage.install()
        fakescanimage.setdevices('epson2:libusb:123:456')
        scanner = ScanimageScannerController()
        assert scanner.device_name == 'epson2:libusb:123:456'

    def test_init_no_scanner(self, fakescanimage):
        fakescanimage.install()
        fakescanimage.setdevices()
        with pytest.raises(ScannerError, match='No scanner detected'):
            ScanimageScannerController()

    def test_init_multiple_scanners(self, fakescanimage):
        fakescanimage.install()
        fakescanimage.setdevices(
            'epson2:libusb:123:456', 'epson2:libusb:321:654'
        )
        with pytest.raises(
            ScannerError,
            match=r'Scanimage detected multiple scanners'
        ):
            ScanimageScannerController()

    def test_init_error(self, fakescanimage):
        fakescanimage.install()
        fakescanimage.seterror('bla')
        with pytest.raises(ScannerError, match='bla'):
            ScanimageScannerController()

    @pytest.mark.usefixtures('usbscanner')
    def test_scan_output(self):
        scanner = ScanimageScannerController()
        data = scanner.scan()
        img = Image.open(BytesIO(data))
        assert img.format == 'TIFF'
        assert img.width == 4800
        assert img.height == 6000
        assert img.mode == PIL_8BITS_BW_MODE

    @pytest.mark.usefixtures('usbscanner')
    def test_scan_compression(self):
        scanner = ScanimageScannerController()
        data_cmp = scanner.scan(compress=True)
        data_raw = scanner.scan(compress=False)
        img_cmp = Image.open(BytesIO(data_cmp))
        img_raw = Image.open(BytesIO(data_raw))
        assert img_cmp.tobytes() == img_raw.tobytes()

    def test_scan_error(self, fakescanimage):
        fakescanimage.install()
        scanner = ScanimageScannerController()
        fakescanimage.seterror('Whoops')
        with pytest.raises(ScannerError, match='Whoops'):
            scanner.scan()
