#!/usr/bin/python2

import parkbenchcommon.beaconbroadcaster

broadcaster = parkbenchcommon.beaconbroadcaster.BeaconBroadcaster(
    'test_program', 'test_beacon', 1000, 1000)

broadcaster.send()
