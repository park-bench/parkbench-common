#!/usr/bin/env python2

import confighelper
import ConfigParser
import logging
import unittest

class ConfigValidationTests(unittest.TestCase):
    def setUp(self):
        # Load config file
        # Pass it to configParser
        self.config_file = ConfigParser.RawConfigParser()
        self.config_file.read('./tests/data/config.txt')

        log_file = '/dev/null'
        log_level = 'critical'
        self.config_helper = confighelper.ConfigHelper()

        self.config_helper.configure_logger(log_file, log_level)
        self.logger = logging.getLogger()


    def test_int_is_positive(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(self.config_file, 'negative_int', lower_bound=0)

    def tearDown(self):
        # Close config file
        pass

if __name__ == '__main__':
    unittest.main()
