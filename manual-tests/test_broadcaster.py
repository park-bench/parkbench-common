#!/usr/bin/python2

import parkbenchcommon.broadcaster

broadcaster = parkbenchcommon.broadcaster.Broadcaster(
    'test_program', 'test_broadcast', 1000, 1000)

broadcaster.issue()
