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

""" Provides the broadcasting component of a filesystem-based IPC mechanism."""

__all__ = ['BroadcasterBroadcastException',
           'BroadcasterInitException',
           'Broadcaster']

import datetime
import logging
import os
import stat
import tmpfs

GROUP_RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR | stat.S_IXGRP | stat.S_IRGRP
GROUP_RO_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IRGRP
RW_MODE = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR

BROADCAST_PATH = '/var/spool/'
TMPFS_SIZE = '1M'

class BroadcasterBroadcastException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to issue a broadcast."""

class BroadcasterInitException(Exception):
    """ This exception is raised when a BeaconBroadcaster object fails to initialize."""

class Broadcaster(object):
    """ Provides the broadcasting component of a filesystem-based IPC mechanism."""

    def __init__(self, program_name, broadcast_name, uid, gid):
        """ Initial configuration of the broadcast directory. This must be done as root.

        program_name: The name of the program issuing the broadcast.
        broadcast_name: The name of the broadcast to issue.
        uid: The UID of the calling program
        gid: The GID of the calling program
        """

        self.logger = logging.getLogger(__name__)

        self.logger.debug("Initializing broadcaster for broadcast %s from program %s.",
                          broadcast_name, program_name)

        self.broadcast_path = os.path.join(BROADCAST_PATH, program_name, broadcast_name)
        self.program_name = program_name
        self.broadcast_name = broadcast_name

        tmpfs_path = os.path.join(BROADCAST_PATH, program_name)
        tmpfs.mount_tmpfs(tmpfs_path, TMPFS_SIZE)

        self._create_directory(self.broadcast_path)
        self._set_file_permissions(self.broadcast_path, GROUP_RW_MODE, uid, gid)

        self.logger.info("Broadcaster for eacon %s from program %s initialized.",
                         broadcast_name, program_name)

    def issue(self):
        """ Place a new file in the broadcast directory. Will raise an exception if it fails."""
        self.logger.info(
            "Sending broadcast %s for program %s.", self.broadcast_name, self.program_name)
        now = datetime.datetime.now().isoformat()
        random_number = os.urandom(16).encode('hex')

        broadcast_filename = '%s---%s' % (now, random_number)
        final_path = os.path.join(self.broadcast_path, broadcast_filename)

        try:
            previous_broadcasts = os.listdir(self.broadcast_path)
            open(final_path, 'a').close()

            for broadcast_file in previous_broadcasts:
                os.remove(os.path.join(self.broadcast_path, broadcast_file))

        except Exception as exception:
            message = 'Could not create broadcast file for broadcast %s, program %s. %s:%s' % (
                self.broadcast_name, self.program_name, type(exception).__name__,
                str(exception))
            self.logger.critical(message)
            raise BroadcasterBroadcastException(message)

    def _set_file_permissions(self, path, mode, uid, gid):
        """ Sets permissions for a file. Will raise an exception if it fails.

        path: The file to modify
        mode: The mode to set
        uid: The owner to set
        gid: The group to set
        """
        try:
            os.chown(path, uid, gid)
            # Set permissions to xrw-------
            os.chmod(path, mode)

        except Exception as exception:
            self.logger.critical('Could not set permissions for file %s for broadcast %s for'
                                 'program %s. %s: %s.', path, self.broadcast_name,
                                 self.program_name, type(exception).__name__, str(exception))
            raise BroadcasterInitException

    def _create_directory(self, path):
        """ Create a directory while handling errors. Will raise an exception if it fails.

        path: The directory to create
        """
        path = os.path.abspath(path)
        if not os.path.isdir(path):
            try:
                os.makedirs(path)

            except Exception as exception:
                message = 'Could not create directory %s for broadcast %s, program %s. %s:%s' % (
                    path, self.broadcast_name, self.program_name,
                    type(exception).__name__, str(exception))
                self.logger.critical(message)
                raise BroadcasterInitException(message)
