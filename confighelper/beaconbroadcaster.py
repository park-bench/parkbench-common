""" Provides the broadcasting component of a a filesystem-based IPC mechanism."""

import datetime
import logging
import os
import stat
import tmpfs

GROUP_RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXGRP | stat.S_IRGRP
GROUP_RO_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IRGRP
RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR

BEACON_PATH = '/var/spool/'
TMPFS_SIZE = '1M'

class BeaconBroadcasterInitException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to initialize."""

class BeaconBroadcasterBroadcastException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to send a beacon."""

class BeaconBroadcaster(object):
    """ Provides the broadcasting component of a filesystem-based IPC mechanism."""

    def __init__(self, program_name, beacon_name, uid, gid):
        """ Initial configuration of the beacon directory. This must be done as root.

        program_name: The name of the program broadcasting the beacon.
        beacon_name: The name of the beacon to broadcast.
        uid: The UID of the calling program
        gid: The GID of the calling program
        """

        self.logger = logging.getLogger(__name__)
        self.beacon_path = '%s/%s/%s/' % (BEACON_PATH, program_name, beacon_name)
        self.partial_beacon_path = '%s/partial/' % self.beacon_path
        self.program_name = program_name
        self.beacon_name = beacon_name

        self._create_directory(self.beacon_path)
        self._set_directory_permissions(self.beacon_path, GROUP_RW_MODE, uid, gid)

        # TODO: Make tmpfs.py report errors properly.
        tmpfs.mount_tmpfs(self.beacon_path, TMPFS_SIZE)

        self._create_directory(self.partial_beacon_path)
        self._set_directory_permissions(self.partial_beacon_path, RW_MODE, uid, gid)

    def send(self):
        """ Place a new file in the beacon directory. Will raise an exception if it fails."""
        now = datetime.isoformat()
        random_number = os.urandom(16).encode(hex)

        beacon_filename = '%s---%s' % (now, random_number)
        partial_path = os.path.join(self.partial_beacon_path, beacon_filename)
        final_path = os.path.join(self.beacon_path, beacon_filename)

        try:
            open(partial_path, 'a', mode=GROUP_RO_MODE).close()
            os.rename(partial_path, final_path)

        except Exception as exception:
            self.logger.critical(
                'Could not create beacon file for beacon %s for program %s. %s: %s.',
                self.beacon_name, self.program_name, type(exception).__name__,
                str(exception))
            raise BeaconBroadcasterBroadcastException

    def _set_directory_permissions(self, path, mode, uid, gid):
        try:
            os.chown(path, uid, gid)
            # Set permissions to xrw-------
            os.chmod(path, mode)

        except Exception as exception:
            self.logger.critical('Could not set permissions for file %s for beacon %s for'
                                 'program %s. %s: %s.', path, self.beacon_name,
                                 self.program_name, type(exception).__name__, str(exception))
            raise BeaconBroadcasterInitException

    def _create_directory(self, path):
        if not os.path.isdir(path):
            try:
                os.mkdir(path)

            except Exception as exception:
                self.logger.critical(
                    'Could not create directory %s for beacon %s for program %s. %s: %s.',
                    path, self.beacon_name, self.program_name,
                    type(exception).__name__, str(exception))
                raise BeaconBroadcasterInitException
