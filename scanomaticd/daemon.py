from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler


class ScanDaemon:
    JOBID_SCANNING = 'scanning'

    def __init__(self, scanningjob, scancommand, scheduler=BlockingScheduler):
        self._scheduler = scheduler()
        self._scancommand = scancommand

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

    def start(self):
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()
