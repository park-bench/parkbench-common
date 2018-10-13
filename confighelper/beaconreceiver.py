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

""" Provides the receiving component of a filesystem-based IPC mechanism."""

import os
import logging
import time
import tmpfs

BEACON_PATH = '/var/spool/'
TMPFS_SIZE = '1M'

class BeaconCheckError(Exception):
    """ This exception is raised when an error is encountered while attempting to check a
    beacon.
    """

class BeaconReceiver(object):
    """ Provides the receiving component of a filesystem-based IPC mechanism.

    program_name: The name of the program that broadcasts this beacon
    beacon_name: The name of this beacon
    check_intveral: The number of seconds to wait in between re-reading the filesystem
    """
    def __init__(self, program_name, beacon_name, check_interval):
        self.logger = logging.getLogger(__name__)

        self.beacon_name = beacon_name
        self.program_name = program_name
        self.tmpfs_path = os.path.join(BEACON_PATH, program_name)
        self.beacon_path = os.path.join(BEACON_PATH, program_name, beacon_name)
        self.last_beacon_time = None
        self.next_check_time = time.time()
        self.check_interval = check_interval

        tmpfs.mount_tmpfs(self.tmpfs_path, TMPFS_SIZE)

        self.logger.info('The reciever for beacon %s from program %s has been initialized.',
                         beacon_name, program_name)

    def check(self):
        """ Check if a new beacon has been broadcast.

        Returns True if a new beacon has been broadcast. Returns False otherwise.
        """
        beacon_updated = False

        if time.time() > self.next_check_time:
            latest_beacon_time = self._read_beacon_time()

            if latest_beacon_time > self.last_beacon_time:
                self.logger.debug('The beacon %s from program %s has been received.',
                                  self.beacon_name, self.program_name)
                self.logger.debug('Updating last beacon time from %s to %s.',
                                  self.last_beacon_time, latest_beacon_time)
                self.last_beacon_time = latest_beacon_time

                beacon_updated = True

            self.next_check_time = self.next_check_time + self.check_interval
        return beacon_updated

    def _read_beacon_time(self):
        """ Retrieve the most recent time on which a beacon has been written.

        Returns an ISO formatted timestamp if a beacon file exists. If no files exist, None
        is returned.
        """
        beacon_time = None
        if os.path.isdir(self.beacon_path):
            if tmpfs.path_is_tmpfs_mountpoint(self.tmpfs_path):
                file_list = os.listdir(self.beacon_path)
                latest_file_name = sorted(file_list, reverse=True)[0]
                beacon_time = latest_file_name.split('---')[0]

            else:
                raise BeaconCheckError('%s is not a tmpfs mountpoint.' % self.beacon_path)

        return beacon_time
