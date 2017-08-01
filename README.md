# confighelper

_confighelper_ is a library to help parse Parkbench configuration files. Configuration files are assumed to be in the format defined by the ConfigParser Python module. This library is **not** a general purpose library and is only intended for use by the Parkbench project.

confighelper is licensed under the GNU GPLv3.

Bug fixes are welcome!

## Prerequisites

This software is currently only supported on Ubuntu 14.04 and may not be ready for use in a production environment.

The only current method of installation for our software is building and
installing your own debian package. We make the following assumptions:

* You are already familiar with using a Linux terminal.
* You already know how to use GnuPG.
* You are already somewhat familiar with using debuild.

## Steps to Build and Install

1. Clone the latest *release tag*. (Do not clone the master branch. `master` may not be stable.)
2. Use `debuild` in the project root directory to build the package.
3. Use `dpkg -i` to install the package.
4. Use `apt-get -f install` to resolve any missing dependencies.

The library should now be available for other Parkbench projects to use.
