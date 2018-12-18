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

"""Provides a class for managing ramdisks."""

__all__ = ['Ramdisk', 'RamdiskMountError', 'RamdiskOptionError']

import logging
import os
import subprocess

# This is easy to edit, just in case someone wants a disk measurable in terabytes.
VALID_TMPFS_SIZE_SUFFIXES = ['k', 'm', 'g', '%']

class RamdiskMountError(Exception):
    """Raised when a ramdisk mount operation fails."""


class RamdiskOptionError(ValueError):
    """Raised when an option for a ramdisk mount is invalid."""


class Ramdisk:
    """A class for managing ramdisks."""

    def __init__(self, path):
        """Constructor.

        path: A string indicating the path where the ramdisk will be mounted.
        """
        self.logger = logging.getLogger(__name__)

        # The mount command outputs the canonical path of all mountpoints. Python calls this
        #   realpath.
        self.path = os.path.realpath(path)

    def mount(self, size, uid, gid, mode):
        """Mounts the ramdisk. Raises an exception on failure, and does nothing if the disk
        is already mounted.

        size: The size of the ramdisk to be mounted. This should be a string representing a
          number of bytes, and may include the single-character suffixes k, m, g, or % for
          kibibytes, mebibytes, gibibytes, or percentage of physical RAM, respectively.
        uid: The system user ID that should own the mount directory.
        gid: The system group ID that should be associated with the mount directory.
        mode: The mode of the mount directory access permissions. This should be a decimal
          integer. ex: 511, not 777.
          Note: This integer is most easily obtained by ORing the appropriate permission
          flags from the stat module.
        """

        # Since size should be an integer with a single character suffix, we validate only
        #   the integer part by including all but the last character of the string.
        self._validate_size_option(size)
        self._validate_integer_option('uid', uid)
        self._validate_integer_option('gid', gid)
        self._validate_integer_option('mode', mode)

        # TODO #16: On Python 3 migration, oct() will break this code.
        mount_options = 'size=%s,uid=%s,gid=%s,mode=%s' % (size, uid, gid, oct(mode))

        if not self.is_mounted():
            if os.path.isfile(self.path):
                raise RamdiskMountError(
                    'Could not mount ramdisk on %s. Specified path is a file.' % self.path)

            if not os.path.isdir(self.path):
                raise RamdiskMountError(
                    'Could not mount ramdisk on %s. Specified path does not exist.' % \
                    self.path)

            if not os.listdir(self.path) == []:
                self.logger.warning('Ramdisk mountpoint %s is not empty.', self.path)

            return_code = subprocess.call(
                ['mount', '-t', 'tmpfs', '-o', mount_options, 'none', self.path])

            if not self.is_mounted():
                # TODO #16: Implement exception chaining when we move to Python 3.
                raise RamdiskMountError(
                    'Could not mount ramdisk on %s. Mount return code was %s.' %
                    (self.path, return_code))

    def is_mounted(self):
        """Checks whether the ramdisk is mounted.

        Returns True if is mounted, returns False otherwise.
        """
        return 'none on %s type tmpfs' % self.path in str(subprocess.check_output('mount'))

    def _validate_integer_option(self, option_name, value):
        """Raises an exception and writes a log message if the given value is not an
        integer.
        """
        if not self._is_integer(value):
            message = 'The value %s for ramdisk mount option %s is not formatted ' \
                'correctly.' % (value, option_name)
            self.logger.error(message)
            raise RamdiskOptionError(message)

    def _validate_size_option(self, size_input):
        """Checks whether a size definition is formatted correctly. If it is not, this
        method will raise an exception.

        size_input: A string to be validated.
        """
        if not self._is_integer(size_input):
            if not (size_input[-1:] in VALID_TMPFS_SIZE_SUFFIXES \
                and self._is_integer(size_input[:-1])):
                message = 'The value %s for ramdisk mount option size is not ' \
                        'formatted correctly.' % size_input
                self.logger.error(message)
                raise RamdiskOptionError(message)

    def _is_integer(self, value):
        """Checks a string for integer-ness.

        Returns True if it can be an integer, returns False otherwise.
        """
        try:
            int(value)
            return True

        except ValueError:
            return False
