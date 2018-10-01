""" Provides the receiving component of a filesystem-based IPC mechanism."""

import os
import logging
import time
import tmpfs

BEACON_PATH = '/var/spool/'

class BeaconReceiver(object):
    """ Provides the receiving component of a filesystem-based IPC mechanism.

    program_name: The name of the program that broadcasts this beacon
    beacon_name: The name of this beacon
    check_intveral: The number of seconds to wait in between re-reading the filesystem
    """
    def __init__(self, program_name, beacon_name, check_interval):
        self.logger = logging.getLogger(__name__)

        self.beacon_name = beacon_name
        self.program_name = program_name
        self.beacon_path = '%s/%s/%s/' % (BEACON_PATH, program_name, beacon_name)
        self.last_beacon_time = None
        self.next_check_time = time.time()
        self.check_interval = check_interval

        self.logger.info('The reciever for beacon %s from program %s has been initialized.',
                         beacon_name, program_name)

    def check(self):
        """ Check if a new beacon has been broadcast.

        Returns True if a new beacon has been broadcast. Returns False otherwise.
        """
        beacon_updated = False

        if time.time() > self.next_check_time:
            latest_beacon_time = self._read_beacon_time()

            if latest_beacon_time >= self.last_beacon_time:
                self.last_beacon_time = latest_beacon_time
                self.logger.debug('The beacon %s from program %s has been received.',
                                  self.beacon_name, self.program_name)

            self.next_check_time = self.next_check_time + self.check_interval
        return beacon_updated

    def _read_beacon_time(self):
        """ Retrieve the most recent time on which a beacon has been written.

        Returns an ISO formatted timestamp if a beacon file exists. If no files exist, None
        is returned.
        """
        beacon_time = None
        if os.path.isdir(self.beacon_path):
            if tmpfs.path_is_tmpfs_mountpoint(self.beacon_path):
                file_list = os.listdir(self.beacon_path)
                latest_file_name = sorted(file_list)[0]
                beacon_time = latest_file_name.split('---')[0]

        return beacon_time
