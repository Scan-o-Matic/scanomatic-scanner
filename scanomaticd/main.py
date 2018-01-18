from datetime import datetime, timedelta
import logging

from .daemon import ScanDaemon
from .scannercontroller import ScanimageScannerController, ScannerError
from .scanning import ScanCommand, ScanningJob
from .scanstore import ScanStore
from .heartbeat import HeartbeatCommand, HeartbeatJob

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


if __name__ == '__main__':
    LOG.info('Starting scanomaticd')

    scanjob = ScanningJob(
        id='fake',
        interval=timedelta(minutes=5),
        end_time=datetime.now() + timedelta(minutes=15),
    )
    try:
        scanner = ScanimageScannerController()
    except ScannerError as error:
        LOG.critical("Can't initialise scanner controller: %s", str(error))
        exit(1)
    store = ScanStore('/var/scanomaticd/scans')
    scancommand = ScanCommand(scanjob, scanner, store)

    heartbeatjob = HeartbeatJob(
        id='fakebeat',
        interval=timedelta(seconds=1)
    )
    heartbeatcommand = HeartbeatCommand(heartbeatjob, scanner)

    daemon = ScanDaemon(scanjob, scancommand, heartbeatcommand, heartbeatjob)
    daemon.start()
