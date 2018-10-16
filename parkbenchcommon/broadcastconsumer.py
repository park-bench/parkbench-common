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

""" Provides the consuming component of a filesystem-based IPC mechanism."""

import os
import logging
import time
import tmpfs

__all__ = ['BroadcastCheckError', 'BroadcastConsumer']

BROADCAST_PATH = '/var/spool/'
TMPFS_SIZE = '1M'

class BroadcastCheckError(Exception):
    """ This exception is raised when an error is encountered while attempting to check a
    broadcast.
    """

class BroadcastConsumer(object):
    """ Provides the consuming component of a filesystem-based IPC mechanism.

    program_name: The name of the program that broadcasts this broadcast
    broadcast_name: The name of this broadcast
    check_intveral: The number of seconds to wait in between re-reading the filesystem
    """
    def __init__(self, program_name, broadcast_name, check_interval):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing consumer for broadcast %s from program %s.",
                          broadcast_name, program_name)

        self.broadcast_name = broadcast_name
        self.program_name = program_name
        self.tmpfs_path = os.path.join(BROADCAST_PATH, program_name)
        self.broadcast_path = os.path.join(BROADCAST_PATH, program_name, broadcast_name)
        self.last_broadcast_time = None
        self.next_check_time = time.time()
        self.check_interval = check_interval

        tmpfs.mount_tmpfs(self.tmpfs_path, TMPFS_SIZE)

        self.logger.info(
            'The consumer for broadcast %s from program %s has been initialized.',
            broadcast_name, program_name)

    def check(self):
        """ Check if a new broadcast has been issued.

        Returns True if a new broadcast has been issued. Returns False otherwise.
        """
        broadcast_updated = False

        if time.time() > self.next_check_time:
            latest_broadcast_time = self._read_broadcast_time()

            if latest_broadcast_time > self.last_broadcast_time:
                self.logger.info('The broadcast %s from program %s has been consumed.',
                                 self.broadcast_name, self.program_name)
                self.logger.debug('Updating last broadcast time from %s to %s.',
                                  self.last_broadcast_time, latest_broadcast_time)
                self.last_broadcast_time = latest_broadcast_time

                broadcast_updated = True

            self.next_check_time = self.next_check_time + self.check_interval
        return broadcast_updated

    def _read_broadcast_time(self):
        """ Retrieve the most recent time on which a broadcast has been written.

        Returns an ISO formatted timestamp if a broadcast file exists. If no files exist,
        None is returned.
        """
        broadcast_time = None
        if os.path.isdir(self.broadcast_path):
            if tmpfs.path_is_tmpfs_mountpoint(self.tmpfs_path):
                file_list = os.listdir(self.broadcast_path)
                latest_file_name = sorted(file_list, reverse=True)[0]
                broadcast_time = latest_file_name.split('---')[0]

            else:
                raise BroadcastCheckError('%s is not a tmpfs mountpoint.' % self.tmpfs_path)

        return broadcast_time
