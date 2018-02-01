import io
import logging
import subprocess
import warnings

LOG = logging.getLogger(__name__)

SCANIMAGE_OPTS = [
    '--source', 'TPU8x10',
    '--format', 'tiff',
    '--resolution', '600',
    '--mode', 'Gray',
    '-l', '0',
    '-t', '0',
    '-x', '203.2',
    '-y', '254',
    '--depth', '8',
]


class ScannerError(Exception):
    pass


class ScanimageScannerController:
    def __init__(self):
        devices = self._get_devices()
        if len(devices) == 1:
            self.device_name = devices[0]
        elif len(devices) > 1:
            raise ScannerError(
                'Scanimage detected multiple scanners: {}'
                .format(' '.join(devices))
            )
        else:
            raise ScannerError('No scanner detected')

    def scan(self):
        return self._run_scanimage(
            '-d', self.device_name, *SCANIMAGE_OPTS).stdout

    def _get_devices(self):
        proc = self._run_scanimage('-f', '%d%n')
        return [dev for dev in proc.stdout.decode('ascii').split()]

    def _run_scanimage(self, *args):
        command = ['scanimage', *args]
        LOG.debug('running scanimage command: %s', command)
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            proc.check_returncode()
        except subprocess.CalledProcessError:
            raise ScannerError(proc.stderr.decode('utf-8'))
        return proc
