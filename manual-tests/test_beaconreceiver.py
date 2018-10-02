#!/usr/bin/python2

import logging
import time
import confighelper.beaconreceiver

logging.basicConfig(level=logging.DEBUG)
print(logging.handlers)

receiver = confighelper.beaconreceiver.BeaconReceiver('test_program', 'test_beacon', 1)

while True:
    if receiver.check():
        print('Beacon received.')
    else:
        print('Nothing new.')

    time.sleep(2)
