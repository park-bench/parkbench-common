# Copyright 2017-2018 Joel Allen Luellwitz and Andrew Klapp
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Provides the broadcasting component of a a filesystem-based IPC mechanism."""

__all__ = ['BeaconBroadcasterBroadcastException',
           'BeaconBroadcasterInitException',
           'BeaconBroadcaster']

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

class BeaconBroadcasterBroadcastException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to send a beacon."""

class BeaconBroadcasterInitException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to initialize."""

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
        self.program_name = program_name
        self.beacon_name = beacon_name

        # TODO: Make tmpfs.py report errors properly.
        tmpfs_path = os.path.join(BEACON_PATH, program_name)
        tmpfs.mount_tmpfs(tmpfs_path, TMPFS_SIZE)

        self._create_directory(self.beacon_path)
        self._set_directory_permissions(self.beacon_path, GROUP_RW_MODE, uid, gid)

    def send(self):
        """ Place a new file in the beacon directory. Will raise an exception if it fails."""
        now = datetime.datetime.now().isoformat()
        random_number = os.urandom(16).encode('hex')

        beacon_filename = '%s---%s' % (now, random_number)
        final_path = os.path.join(self.beacon_path, beacon_filename)

        try:
            previous_beacons = os.listdir(self.beacon_path)
            open(final_path, 'a').close()

            for beacon_file in previous_beacons:
                os.remove(os.path.join(self.beacon_path, beacon_file))

        except Exception as exception:
            message = 'Could not create beacon file for beacon %s, program %s. %s:%s' % (
                self.beacon_name, self.program_name, type(exception).__name__,
                str(exception))
            self.logger.critical(message)
            raise BeaconBroadcasterBroadcastException(message)

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
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            try:
                os.makedirs(path)

            except Exception as exception:
                message = 'Could not create directory %s for beacon %s, program %s. %s:%s' % (
                    path, self.beacon_name, self.program_name,
                    type(exception).__name__, str(exception))
                self.logger.critical(message)
                raise BeaconBroadcasterInitException(message)
