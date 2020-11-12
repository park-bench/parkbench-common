# parkbench-common

_parkbench-common_ is a collection of helper modules for Parkbench programs. These helper
modules are **not** general purpose libraries and are only intended for use by the Parkbench
project.

parkbench-common is licensed under the GNU GPLv3.

This software is still in _beta_ and may not be ready for use in a production environment.

Bug fixes are welcome!

## Included Modules

### ConfigHelper
`ConfigHelper` is a helper class for `ConfigParser`. It includes expanded option validation,
and makes some assumptions specific to Parkbench projects.

### Ramdisk
`ramdisk` is a very simple module for mounting filesystems on ramdisks. It currently uses
tmpfs.

### Broadcaster
`Broadcaster` provides the broadcasting component for _broadcasts_, a filesystem-based IPC
mechanism.

### BroadcastConsumer
`BroadcastConsumer` provides the receiving component for _broadcasts_, a filesystem-based IPC
mechanism.

## Prerequisites

This software is currently only supported on Ubuntu 18.04.

Currently, the only supported method for installation of this project is building and
installing a Debian package. The rest of these instructions make the following assumptions:

*   You are familiar with using a Linux terminal.
*   You are somewhat familiar with using `debuild`.
*   You are familiar with using `git` and GitHub.
*   `debhelper`, `devscripts`, `python3-all`, and `python3-setuptools` are installed on your
    build server.
*   You are familiar with GnuPG (for deb signing).

## Steps to Build and Install

1.  Clone the repository and checkout the latest release tag. (Do not build against the
    `master` branch. The `master` branch might not be stable.)
2.  Run `debuild` in the project root directory to build the package.
3.  Run `apt install /path/to/package.deb` to install the package.

The helper modules should now be available for other Parkbench projects to use.
