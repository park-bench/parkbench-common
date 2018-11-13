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

"""Provides the broadcasting component of a filesystem-based IPC mechanism."""

__all__ = ['BroadcasterIssueException',
           'BroadcasterInitException',
           'Broadcaster']

import datetime
import logging
import os
import stat
import traceback
from parkbenchcommon import daemonhelper
from parkbenchcommon import ramdisk

SPOOL_PATH = '/var/spool'
RAMDISK_SIZE = '1M'
# drwx--x---
PROGRAM_DIR_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IXGRP
# drwxr-x---
BROADCAST_DIR_MODE = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IXGRP

class BroadcasterIssueException(Exception):
    """This exception is raised when a Broadcaster object fails to issue a broadcast."""

class BroadcasterInitException(Exception):
    """This exception is raised when a Broadcaster object fails to initialize."""

class Broadcaster(object):
    """Provides the broadcasting component of a filesystem-based IPC mechanism."""

    def __init__(self, program_name, broadcast_name, uid, gid):
        """Initial configuration of the broadcast directory. This must be done as root. This
        constructor mounts a ramdisk and creates any necessary spool rirectories with
        proper permissions. Any failure to create directories will raise exceptions.

        program_name: The name of the program issuing the broadcast.
        broadcast_name: The name of the broadcast to issue.
        uid: The UID of the calling program.
        gid: The GID of the calling program.
        """

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initializing broadcaster for broadcast %s from program %s.",
                          broadcast_name, program_name)

        self.program_name = program_name
        self.broadcast_name = broadcast_name

        program_path = os.path.join(SPOOL_PATH, program_name)
        ramdisk_path = os.path.join(program_path, 'ramdisk')
        self.ramdisk = ramdisk.Ramdisk(ramdisk_path, RAMDISK_SIZE, uid, gid,
                                       PROGRAM_DIR_MODE)
        self.broadcast_path = os.path.join(ramdisk_path, 'broadcast')


        self.logger.debug('Creating broadcast directories for program %s.', program_name)
        daemonhelper.create_directories(
            SPOOL_PATH, [program_path, ramdisk_path], uid, gid, PROGRAM_DIR_MODE)

        self.ramdisk.mount()
        daemonhelper.create_directories(
            ramdisk_path, [self.broadcast_path], uid, gid, BROADCAST_DIR_MODE)

        self.logger.info("Broadcaster %s from program %s initialized.",
                         broadcast_name, program_name)

    def issue(self):
        """Issues a new broadcast overriding any prior broadcast. Will raise an exception if
        it fails.
        """
        self.logger.info(
            "Issuing broadcast %s for program %s.", self.broadcast_name, self.program_name)
        now = datetime.datetime.now().isoformat()
        random_number = os.urandom(16).encode('hex')

        broadcast_filename = '%s-%s-%s' % (self.broadcast_name, now, random_number)
        broadcast_pathname = os.path.join(self.broadcast_path, broadcast_filename)

        try:
            previous_broadcasts = os.listdir(self.broadcast_path)
            open(broadcast_pathname, 'a').close()

            for broadcast_file in previous_broadcasts:
                os.remove(os.path.join(self.broadcast_path, broadcast_file))

        except Exception as exception:
            message = \
                'Could not create broadcast file for broadcast %s, program %s. %s: %s\n%s' \
                % (self.broadcast_name, self.program_name, type(exception).__name__,
                   str(exception), traceback.format_exc())
            self.logger.error(message)
            # TODO: Implement exception chaining when we move to Python 3.
            raise BroadcasterIssueException(message)
