from apscheduler.schedulers.blocking import BlockingScheduler


class ScanDaemon:
    def __init__(
            self, scanningjob, scancommand, heartinterval, heartcommand,
            scheduler=BlockingScheduler):
        self._scheduler = scheduler()

        self._scancommand = scancommand
        self._scheduler.add_job(
            scancommand.execute,
            'interval',
            seconds=scanningjob.interval.total_seconds(),
            end_date=scanningjob.end_time,
        )

        self._scheduler.add_job(
            heartcommand.execute,
            'interval',
            seconds=heartinterval.total_seconds(),
        )

    def start(self):
        self._scancommand.execute()
        self._scheduler.start()

    def stop(self):
        self._scheduler.shutdown()
