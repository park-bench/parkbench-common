# Copyright 2018-2019 Joel Allen Luellwitz and Emily Frost
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

"""Provides daemon-related helper functions for Parkbench projects."""

import os

def create_directories(system_path, program_dirs, uid, gid, mode,
                       keep_existing_permissions=False):
    """Creates directories if they do not exist and sets the specified ownership and
    permissions.

    system_path: The system path that the directories should be created under.  These are
      assumed to already exist. The ownership and permissions on these directories are not
      modified.
    program_dirs: A string representing additional directories that should be created under
      the system path that should take on the following ownership and permissions.
    uid: The system user ID that should own the directories.
    gid: The system group ID that should be associated with the directories.
    mode: The access mode of the directories to be created.
    keep_existing_permissions: If True, do not modify permissions or ownership of any
      directories that already exist.
    """

    path = system_path
    for directory in program_dirs.strip('/').split('/'):
        path = os.path.join(path, directory)
        new_directory = False
        if not os.path.isdir(path):
            # Will throw exception if file cannot be created.
            os.makedirs(path, mode)
            new_directory = True

        if not keep_existing_permissions or new_directory:
            os.chown(path, uid, gid)
            os.chmod(path, mode)
