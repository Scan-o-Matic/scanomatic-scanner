from datetime import datetime, timezone
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

    def test_put_saves_scanned_data(self, tmpdir, scanstore, scan):
        scanstore.put(scan)
        file = tmpdir.join('abcd_499137600.tiff')
        assert file.check(file=1)
        assert file.read() == 'I am a scan'

    def test_put_saves_metadata(self, tmpdir, scanstore, scan):
        scanstore.put(scan)
        file = tmpdir.join('abcd_499137600.json')
        assert file.check(file=1)
        assert json.load(file) == {
            'jobId': 'abcd',
            'startTime': '1985-10-26T01:20:00+00:00',
            'endTime': '1985-10-26T01:21:00+00:00',
            'digest': 'foo:bar',
        }

    def test_length_empty(self, tmpdir, scanstore):
        assert len(scanstore) == 0

    def test_length_counds_tiff_files(self, tmpdir, scanstore):
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
