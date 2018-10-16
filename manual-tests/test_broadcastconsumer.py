#!/usr/bin/python2

import logging
import time
import parkbenchcommon.broadcastconsumer

logging.basicConfig(level=logging.DEBUG)
print(logging.handlers)

consumer = parkbenchcommon.broadcastconsumer.BroadcastConsumer(
    'test_program', 'test_broadcast', 1)

while True:
    if consumer.check():
        print('Broadcast received.')
    else:
        print('Nothing new.')

    time.sleep(2)
