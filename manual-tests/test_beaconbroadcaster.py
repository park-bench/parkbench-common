#!/usr/bin/python2

import confighelper.beaconbroadcaster

broadcaster = confighelper.beaconbroadcaster.BeaconBroadcaster(
    'test_program', 'test_beacon', 1000, 1000)

broadcaster.send()
