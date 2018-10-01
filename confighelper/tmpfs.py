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
