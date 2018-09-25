# The purpose of this module is to provide a mechanism for NetCheck to broadcast a signal
#   when it connects to a new network.

import datetime
import logging
import os
import stat
import subprocess
import tmpfs

class BeaconBroadcaster(object):
    """ Provides the broadcasting component of a a filesystem-based IPC mechanism."""

    def __init__(self, program_name, beacon_name, uid, gid):
        """ Initial configuration of the beacon directory.

        program_name: The name of the program broadcasting the beacon.
        beacon_name: The name of the beacon to broadcast.
        uid: The UID that NetCheck runs under
        gid: The GID that NetCheck runs under
        """

        self.logger = logging.getLogger(__name__)
        self.beacon_path = '/var/spool/%s/%s/' % (program_name, beacon_name)

        if not os.path.isdir(self.beacon_path):
            try:
                mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXGRP | stat.S_IRGRP
                # The mode argument is not used here because the documentation is unclear about
                #   when it will not work.
                os.makedirs(self.beacon_path)

            except Exception as exception:
                # print a log message and raise an init exception
                pass


        try:
            # Sometime in the near future, this will not run as root.
            os.chown(self.beacon_path, uid, gid)
            # Set permissions to xrwxr------
            os.chmod(self.beacon_path, mode)

        except Exception as exception:
            # print a log message and raise an init exception
            pass

        if not tmpfs.path_is_tmpfs_mountpoint(self.beacon_path):
            tmpfs.mount_tmpfs(self.beacon_path, '25%')

            if not tmpfs.path_is_tmpfs_mountpoint(self.beacon_path):
                # raise an exception
                pass

    def send(self):
        """ Place a new file in the beacon directory. """
        
        beacon_filename = '%s---%s' % (now, random_number)
        # Assemble a filename: <datetime---beacon_name---random number>
        # Write file to a partial directory
        # Move file to beacon directory
        pass
