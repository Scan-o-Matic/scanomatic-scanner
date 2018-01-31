from datetime import datetime, timedelta
import logging
import os

from .apigateway import APIGateway
from .communication import UpdateScanningJobCommand
from .daemon import ScanDaemon
from .heartbeat import HeartbeatCommand
from .scannercontroller import ScanimageScannerController, ScannerError
from .scanning import ScanCommand, ScanningJob
from .scanstore import ScanStore
from .uploading import UploadCommand

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)
LOG = logging.getLogger('scanomaticd')
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
    apigateway = APIGateway(
        os.environ['SCANOMATICD_APIROOT'],
        os.environ['SCANOMATICD_SCANNERID'],
        os.environ['SCANOMATICD_APIUSERNAME'],
        os.environ['SCANOMATICD_APIPASSWORD'],
    )
    scan_command = ScanCommand(scanner, store)
    update_command = UpdateScanningJobCommand(apigateway)
    heartbeat_command = HeartbeatCommand(apigateway)
    upload_command = UploadCommand(apigateway, store)
    daemon = ScanDaemon(
        update_command, scan_command, heartbeat_command, upload_command,
    )
    daemon.start()
