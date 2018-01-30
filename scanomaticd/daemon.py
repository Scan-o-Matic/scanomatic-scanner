from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler


class ScanDaemon:
    JOBID_SCANNING = 'scanning'
    JOBID_UPDATESCANNINGJOB = 'update-scanning-job'
    INTERVAL_UPDATESCANNINGJOB = 60

    def __init__(
        self, updatecommand, scancommand, scheduler=BlockingScheduler
    ):
        self._scheduler = scheduler()
        self._scancommand = scancommand
        self._job = None
        self._scheduler.add_job(
            updatecommand,
            args=(self,),
            trigger='interval',
            coalesce=True,
            id=self.JOBID_UPDATESCANNINGJOB,
            max_instances=1,
            next_run_time=datetime.now(),
            seconds=self.INTERVAL_UPDATESCANNINGJOB,
        )

    def set_scanning_job(self, job):
        if job is None:
            self._scheduler.remove_job(self.JOBID_SCANNING)
        else:
            self._scheduler.add_job(
                self._scancommand,
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
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()

    def get_next_scheduled_scan(self):
        job = self._scheduler.get_job(self.JOBID_SCANNING)
        if job:
            return job.next_run_time
