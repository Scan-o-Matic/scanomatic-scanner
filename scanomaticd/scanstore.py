import json
from pathlib import Path


class ScanStore:
    def __init__(self, dirpath):
        self.path = Path(dirpath)
        self.path.mkdir(parents=True, exist_ok=True)

    def put(self, scan):
        basename = '{jobid}_{timestamp}'.format(
            jobid=scan.job_id,
            timestamp=int(scan.start_time.timestamp()),
        )
        # ⚠ The order of the following calls matter: because we use the image
        # files to determine how many/which scans are in the store, the image
        # file must appear last.
        self._save_metadata(scan, basename)
        self._save_image(scan, basename)

    def _save_metadata(self, scan, basename):
        jsonpath = self.path.joinpath(basename + '.json')
        json_metadata = {
            'jobId': scan.job_id,
            'startTime': scan.start_time.timestamp(),
            'endTime': scan.end_time.timestamp(),
            'digest': scan.digest,
        }
        with jsonpath.open('w') as file:
            json.dump(json_metadata, file)

    def _save_image(self, scan, basename):
        imgpath = self.path.joinpath(basename + '.tiff')
        tmppath = imgpath.with_suffix('.tmp')
        with tmppath.open('wb') as file:
            file.write(scan.data)
        tmppath.rename(imgpath)

    def __len__(self):
        return len(list(self.path.glob('*.tiff')))
