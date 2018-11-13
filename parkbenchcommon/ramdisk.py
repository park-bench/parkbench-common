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

""" Provides helper functions for ramdisk usage."""

__all__ = ['mount_ramdisk', 'path_is_ramdisk_mountpoint', 'RamdiskMountError']

import os
import subprocess

class RamdiskMountError(Exception):
    """ Raised when a ramdisk mount operation fails."""

def path_is_ramdisk_mountpoint(path):
    """ Checks whether a path is a ramdisk mountpoint

    path: The path to check
    Returns True if the path is mounted, False otherwise.
    """
    path = os.path.abspath(path)

    return 'none on %s type tmpfs' % path in str(subprocess.check_output('mount'))

def mount_ramdisk(path, size):
    """ Mounts a ramdisk. Will raise an exception if the mount fails. Does nothing if
        the given path is already a tmpfs ramdisk.

    path: A string indicating the path where the ramdisk will be mounted.
    size: The size of the ramdisk to be mounted. This should be a string representing a
        number of bytes, and may include the single-character suffixes k, m, g, or % for
        kibibytes, mebibytes, gibibytes, or percentage of physical RAM, respectively.
    Does not return anything.
    """

    path = os.path.abspath(path)

    if not path_is_ramdisk_mountpoint(path):
        if not os.path.isfile(path):
            os.mkdir(path)

        if not os.path.isdir(path):
            raise RamdiskMountError(
                'Could not mount tmpfs on %s. %s is not a directory.' % (path, path))
        else:
            if not os.listdir(path) == []:
                raise RamdiskMountError(
                    'Could not mount tmpfs on %s. Directory is not empty.' % path)
            else:
                return_code = subprocess.call(
                    ['mount', '-t', 'tmpfs', '-o', 'size=%s' % size, 'none', path])

                if not path_is_ramdisk_mountpoint(path):
                    # TODO: Implement exception chaining when we move to Python 3.
                    raise RamdiskMountError(
                        'Could not mount tmpfs on %s. Mount return code was %s.' % \
                            (path, return_code))
