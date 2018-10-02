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

""" Provides helper functions for tmpfs usage."""

import subprocess

class TmpfsMountError(Exception):
    """ Raised when a tmpfs mount operation appears to fail."""

def path_is_tmpfs_mountpoint(path):
    """ Checks that a path is mounted as tmpfs.

    path: The path to check
    """

    return 'none on {0} type tmpfs'.format(path) in \
        str(subprocess.check_output('mount'))

def mount_tmpfs(path, size):
    """ Mounts a tmpfs disk.

    path: The path for the disk
    size: The size of the disk
    """

    if not path_is_tmpfs_mountpoint(path):
        # TODO: Use the return code to raise appropriate exceptions.
        subprocess.check_call(['mount', '-t', 'tmpfs', '-size=%s' % size, 'none', path])

    if not path_is_tmpfs_mountpoint(path):
        raise TmpfsMountError('Could not mount tmpfs to %s.' % path)
