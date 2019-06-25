# Copyright 2018 Joel Allen Luellwitz and Emily Frost
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

"""Provides the consuming component of a filesystem-based IPC mechanism."""

import datetime
import os
import logging
import time

__all__ = ['BroadcastCheckError', 'BroadcastConsumer']

SPOOL_PATH = '/var/spool'

class BroadcastCheckError(Exception):
    """This exception is raised when an error is encountered while attempting to check a
    broadcast.
    """

class BroadcastConsumer(object):
    """Provides the consuming component of a filesystem-based IPC mechanism.

    Any beacons broadcast before BroadcastConsumer is instantiated will be ignored.

    program_name: The name of the program that issues this broadcast.
    broadcast_name: The name of this broadcast.
    minimum_delay: The minimum delay in seconds between broadcasts. If a second broadcast
        occurs before minimum_delay has passed, the second broadcast is ignored.
    """
    def __init__(self, program_name, broadcast_name, minimum_delay):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing consumer for broadcast %s from program %s.",
                          broadcast_name, program_name)

        self.broadcast_name = broadcast_name
        self.program_name = program_name
        self.broadcast_path = os.path.join(SPOOL_PATH, program_name, 'ramdisk', 'broadcast')
        self.last_consumed_broadcast = datetime.datetime.now().isoformat()
        self.last_read_broadcast = datetime.datetime.now().isoformat()
        self.next_check_time = time.time()
        self.minimum_delay = minimum_delay


        self.logger.info(
            'The consumer for broadcast %s from program %s has been initialized.',
            broadcast_name, program_name)

    def check(self):
        """Check if a new broadcast has been issued.

        Returns True if a new broadcast has been issued. Returns False otherwise.
        """
        broadcast_updated = False

        latest_broadcast_time = self._read_broadcast_time()

        if latest_broadcast_time is not None:
            if latest_broadcast_time > datetime.datetime.now().isoformat():
                self.logger.warning('Read a %s broadcast from %s from the future and ignored'
                                    ' it. The reported time was %s.', self.broadcast_name,
                                    self.program_name, latest_broadcast_time)

            else:
                if self.next_check_time > time.time():
                    if latest_broadcast_time > self.last_consumed_broadcast:
                        self.logger.debug(
                            'Read a %s broadcast from %s issued during the rate limiting '
                            'delay and ignored it. The reported time was %s.',
                            self.broadcast_name, self.program_name, latest_broadcast_time)
                else:
                    self.logger.info(
                        'The broadcast %s from program %s has been consumed.',
                        self.broadcast_name, self.program_name)
                    self.logger.debug(
                        'Updating last consumed broadcast time from %s to %s.',
                        self.last_consumed_broadcast, latest_broadcast_time)
                    broadcast_updated = True
                    self.next_check_time = time.time() + self.minimum_delay

        return broadcast_updated

    def _read_broadcast_time(self):
        """Retrieve the ISO formatted time from the most recent broadcast.

        Returns a string containing an ISO formatted timestamp if a new broadcast file
            exists. Otherwise, None is returned.
        """
        broadcast_time = None

        if os.path.isdir(self.broadcast_path):
            file_list = os.listdir(self.broadcast_path)
            broadcast_times = []
            for filename in file_list:
                (read_broadcast_name, read_broadcast_time, _) = filename.split('---')
                if read_broadcast_name == self.broadcast_name:
                    broadcast_times.append(read_broadcast_time)

            if broadcast_times:
                current_broadcast_time = sorted(broadcast_times, reverse=True)[0]

                if current_broadcast_time != self.last_read_broadcast:
                    broadcast_time = current_broadcast_time
                    self.last_read_broadcast = current_broadcast_time

        return broadcast_time
