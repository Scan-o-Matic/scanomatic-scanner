import logging
import os

from .apigateway import APIGateway
from .communication import UpdateScanningJobCommand
from .daemon import ScanDaemon
from .heartbeat import HeartbeatCommand
from .scannercontroller import ScanimageScannerController, ScannerError
from .scanning import ScanCommand
from .scanstore import ScanStore
from .uploading import UploadCommand

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
)
LOG = logging.getLogger('scanomaticd')
LOG.setLevel(logging.DEBUG)

LOG.info('Starting scanomaticd')

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
heartbeat_command = HeartbeatCommand(apigateway, store, scanner)
upload_command = UploadCommand(apigateway, store)
daemon = ScanDaemon(
    update_command, scan_command, heartbeat_command, upload_command,
)
daemon.start()
