from datetime import datetime, timedelta
import logging
import os

from .apigateway import APIGateway
from .communication import UpdateScanningJobCommand
from .daemon import ScanDaemon
from .scannercontroller import ScanimageScannerController, ScannerError
from .scanning import ScanCommand, ScanningJob
from .scanstore import ScanStore

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)


if __name__ == '__main__':
    LOG.info('Starting scanomaticd')
    job = ScanningJob(
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
    apigateway = APIGateway(os.environ['SCANOMATICD_APIURL'])
    scannerid = os.environ['SCANOMATICD_SCANNERID']
    scan_command = ScanCommand(scanner, store)
    update_command = UpdateScanningJobCommand(scannerid, apigateway)
    daemon = ScanDaemon(update_command, scan_command)
    daemon.start()
