from datetime import datetime, timezone
from glob import glob
import json

import pytest

from scanomaticd.scanning import Scan
from scanomaticd.scanstore import ScanStore


class TestScanStore:
    @pytest.fixture
    def scanstore(self, tmpdir):
        return ScanStore(str(tmpdir))

    @pytest.fixture
    def scan(self):
        return Scan(
            data=b'I am a scan',
            job_id='abcd',
            start_time=datetime(1985, 10, 26, 1, 20, tzinfo=timezone.utc),
            end_time=datetime(1985, 10, 26, 1, 21, tzinfo=timezone.utc),
            digest='foo:bar',
        )

    @pytest.fixture
    def scan2(self):
        return Scan(
            data=b'I am a scan too!',
            job_id='abcd',
            start_time=datetime(1985, 10, 26, 1, 30, tzinfo=timezone.utc),
            end_time=datetime(1985, 10, 26, 1, 31, tzinfo=timezone.utc),
            digest='foo:baz',
        )

    def _json(self, scan):
        return {
            'jobId': scan.job_id,
            'startTime': scan.start_time.timestamp(),
            'endTime': scan.end_time.timestamp(),
            'digest': scan.digest,
        }

    def test_put_saves_scanned_data(self, tmpdir, scanstore, scan):
        scanstore.put(scan)
        file = tmpdir.join('abcd_499137600.tiff')
        assert file.check(file=1)
        assert file.read() == 'I am a scan'

    def test_put_saves_metadata(self, tmpdir, scanstore, scan):
        scanstore.put(scan)
        file = tmpdir.join('abcd_499137600.json')
        assert file.check(file=1)
        assert json.load(file) == self._json(scan)

    def test_length_empty(self, tmpdir, scanstore):
        assert len(scanstore) == 0

    def test_length_counts_tiff_files(self, tmpdir, scanstore):
        tmpdir.join('file1.tiff').ensure(file=True)
        tmpdir.join('file1.json').ensure(file=True)
        tmpdir.join('file2.tiff').ensure(file=True)
        tmpdir.join('file2.json').ensure(file=True)
        tmpdir.join('file3.tiff').ensure(file=True)
        tmpdir.join('file3.json').ensure(file=True)
        assert len(scanstore) == 3

    def test_creates_directory_if_not_exists(self, tmpdir):
        dir = tmpdir.join('foo', 'bar')
        assert not dir.check(dir=True)
        ScanStore(str(dir))
        assert dir.check(dir=True)

    def test_get_scans_iterator(self, tmpdir, scanstore, scan, scan2):
        with tmpdir.join('scan1.tiff').open(mode='wb') as f:
            f.write(b'I am a scan')
        with tmpdir.join('scan1.json').open(mode='w') as f:
            json.dump(self._json(scan), f)
        with tmpdir.join('scan2.tiff').open(mode='wb') as f:
            f.write(b'I am a scan too!')
        with tmpdir.join('scan2.json').open(mode='w') as f:
            json.dump(self._json(scan2), f)
        assert list(scanstore) == [scan, scan2]

    def test_delete_scan_image(test, tmpdir, scanstore, scan):
        scanstore.put(scan)
        scanstore.delete(scan)
        assert len(glob(str(tmpdir.join('*.tiff')))) == 0

    def test_delete_scan_metadata(test, tmpdir, scanstore, scan):
        scanstore.put(scan)
        scanstore.delete(scan)
        assert len(glob(str(tmpdir.join('*.json')))) == 0

    def test_delete_only_one(test, tmpdir, scanstore, scan, scan2):
        scanstore.put(scan)
        scanstore.put(scan2)
        scanstore.delete(scan)
        assert len(scanstore) == 1
        assert list(scanstore) == [scan2]
