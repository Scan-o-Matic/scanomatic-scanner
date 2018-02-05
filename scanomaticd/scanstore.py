from datetime import datetime, timezone
import json
from pathlib import Path

from .scanning import Scan


class ScanStore:
    def __init__(self, dirpath):
        self.path = Path(dirpath)
        self.path.mkdir(parents=True, exist_ok=True)

    def put(self, scan):
        # ⚠ The order of the following calls matter: because we use the image
        # files to determine how many/which scans are in the store, the image
        # file must appear last.
        self._save_metadata(scan)
        self._save_image(scan)

    def _save_metadata(self, scan):
        jsonpath = self._jsonpath(scan)
        json_metadata = {
            'jobId': scan.job_id,
            'startTime': scan.start_time.timestamp(),
            'endTime': scan.end_time.timestamp(),
            'digest': scan.digest,
        }
        with jsonpath.open('w') as file:
            json.dump(json_metadata, file)

    def _save_image(self, scan):
        imgpath = self._imagepath(scan)
        tmppath = imgpath.with_suffix('.tmp')
        with tmppath.open('wb') as file:
            file.write(scan.data)
        tmppath.rename(imgpath)

    def __len__(self):
        return len(list(self.path.glob('*.tiff')))

    def __iter__(self):
        for imgpath in sorted(self.path.glob('*.tiff')):
            with imgpath.open('rb') as imgf:
                data = imgf.read()
            with imgpath.with_suffix('.json').open('r') as jsonf:
                metadata = json.load(jsonf)
            yield Scan(
                data=data,
                digest=metadata['digest'],
                start_time=self._get_datetime(metadata['startTime']),
                end_time=self._get_datetime(metadata['endTime']),
                job_id=metadata['jobId'],
            )

    def _get_datetime(self, timestamp):
        return datetime.fromtimestamp(timestamp, tz=timezone.utc)

    def delete(self, scan):
        self._imagepath(scan).unlink()
        self._jsonpath(scan).unlink()

    def _jsonpath(self, scan):
        return self._imagepath(scan).with_suffix('.json')

    def _imagepath(self, scan):
        basename = '{jobid}_{timestamp}'.format(
            jobid=scan.job_id,
            timestamp=int(scan.start_time.timestamp()),
        )
        return self.path.joinpath(basename + '.tiff')
