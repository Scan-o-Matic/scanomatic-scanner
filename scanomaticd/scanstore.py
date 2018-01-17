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
        imgpath = self.path.joinpath(basename + '.tiff')
        with imgpath.open('wb') as file:
            file.write(scan.data)
        jsonpath = imgpath.with_suffix('.json')
        json_metadata = {
            'jobId': scan.job_id,
            'startTime': scan.start_time.isoformat(),
            'endTime': scan.end_time.isoformat(),
            'digest': scan.digest,
        }
        with jsonpath.open('w') as file:
            json.dump(json_metadata, file)

    def __len__(self):
        return len(list(self.path.glob('*.tiff')))
