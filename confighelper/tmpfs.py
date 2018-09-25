""" Provides helper functions for tmpfs usage."""

import subprocess

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

    # TODO: Actually process return codes and raise proper exceptions.
    subprocess.call(['mount', '-t', 'tmpfs', '-size=%s' % size, 'none', path])
