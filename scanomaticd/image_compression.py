import logging
import subprocess

LOG = logging.getLogger(__name__)


class CompressionError(Exception):
    pass


def compress_image(stdin):
    command = ['convert', '-', '-compress', 'lzw', '-']
    LOG.debug('running tiff compression: %s', command)
    proc = subprocess.run(
        command,
        input=stdin,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError:
        raise CompressionError(proc.stderr.decode('utf-8'))
    return proc
