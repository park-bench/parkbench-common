""" Provides the broadcasting component of a a filesystem-based IPC mechanism."""

import datetime
import logging
import os
import stat
import tmpfs

GROUP_RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXGRP | stat.S_IRGRP
GROUP_RO_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IRGRP
RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR

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
        self.partial_beacon_path = '%s/partial/' % self.beacon_path

        if not os.path.isdir(self.beacon_path):
            try:
                # The mode argument is not used here because the documentation is unclear about
                #   when it will not work.
                os.mkdir(self.beacon_path)

            except Exception as exception:
                # print a log message and raise an init exception
                pass


        try:
            # Sometime in the near future, this will not run as root.
            os.chown(self.beacon_path, uid, gid)
            # Set permissions to xrwxr------
            os.chmod(self.beacon_path, GROUP_RW_MODE)


        except Exception as exception:
            # print a log message and raise an init exception
            pass

        if not tmpfs.path_is_tmpfs_mountpoint(self.beacon_path):
            tmpfs.mount_tmpfs(self.beacon_path, '25%')

            if not tmpfs.path_is_tmpfs_mountpoint(self.beacon_path):
                # raise an exception
                pass

        try:
            os.mkdir(self.partial_beacon_path)
            os.chown(self.partial_beacon_path, uid, gid)
            # Set permissions to xrw-------
            os.chmod(self.partial_beacon_path, RW_MODE)

        except Exception as exception:
            # Print a log message and raise an init exception
            pass


    def send(self):
        """ Place a new file in the beacon directory. """
        now = datetime.isoformat()
        random_number = os.urandom(16).encode(hex)
        
        beacon_filename = '%s---%s' % (now, random_number)
        partial_path = os.path.join(self.partial_beacon_path, beacon_filename)
        final_path = os.path.join(self.beacon_path, beacon_filename)

        try:
            open(partial_path, 'a', mode=GROUP_RO_MODE).close()
            os.rename(partial_path, final_path)
        except Exception as exception:
            # Print a log message and raise an exception
            pass
