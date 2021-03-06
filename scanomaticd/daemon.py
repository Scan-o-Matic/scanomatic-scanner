from datetime import datetime, timezone
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.base import JobLookupError


class ScanDaemon:
    JOBID_SCANNING = 'scanning'
    JOBID_UPDATESCANNINGJOB = 'update-scanning-job'
    INTERVAL_UPDATESCANNINGJOB = 60
    INTERVAL_UPDATESTATUS = 60
    INTERVAL_UPLOAD = 60

    def __init__(
            self,
            update_command,
            scan_command,
            heartbeat_command,
            upload_command,
            scheduler=BlockingScheduler
    ):
        self._scheduler = scheduler()
        self._start_time = None
        self._scan_command = scan_command
        self._job = None
        self._scheduler.add_job(
            update_command,
            args=(self,),
            trigger='interval',
            coalesce=True,
            id=self.JOBID_UPDATESCANNINGJOB,
            max_instances=1,
            seconds=self.INTERVAL_UPDATESCANNINGJOB,
        )
        self._scheduler.add_job(
            heartbeat_command,
            args=(self,),
            trigger='interval',
            next_run_time=datetime.now(),
            seconds=self.INTERVAL_UPDATESTATUS,
        )
        self._scheduler.add_job(
            upload_command,
            trigger='interval',
            coalesce=True,
            max_instances=1,
            next_run_time=datetime.now(),
            seconds=self.INTERVAL_UPLOAD,
        )

    def set_scanning_job(self, job):
        if job is None:
            try:
                self._scheduler.remove_job(self.JOBID_SCANNING)
            except JobLookupError:
                pass
        else:
            self._scheduler.add_job(
                self._scan_command,
                args=(job,),
                trigger='interval',
                coalesce=True,
                id=self.JOBID_SCANNING,
                max_instances=1,
                next_run_time=datetime.now(),
                replace_existing=True,
                end_date=job.end_time,
                seconds=job.interval.total_seconds(),
            )
        self._job = job

    def get_scanning_job(self):
        return self._job

    def start(self):
        self._start_time = datetime.now(tz=timezone.utc)
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()

    def get_next_scheduled_scan(self):
        job = self._scheduler.get_job(self.JOBID_SCANNING)
        if job:
            return job.next_run_time

    def get_start_time(self):
        return self._start_time
