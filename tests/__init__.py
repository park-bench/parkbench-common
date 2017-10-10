#!/usr/bin/env python2

import confighelper
import ConfigParser
import logging
import unittest

config_file_path='./tests/data/config.txt'

class ConfigValidationTests(unittest.TestCase):
    def setUp(self):
        # Load config file
        # Pass it to configParser
        self.config_file = ConfigParser.RawConfigParser()
        self.config_file.read(config_file_path)

        log_file = '/dev/null'
        log_level = 'critical'
        self.config_helper = confighelper.ConfigHelper()

        self.config_helper.configure_logger(log_file, log_level)
        self.logger = logging.getLogger()

    def test_int_exists(self):
        result = self.config_helper.verify_integer_exists(self.config_file, 'int_1')
        self.assertEqual(1, result)

    # This method does not throw an exception, it exits instead. The next release
    #   will solve this issue.
#    def test_integer_rejects_float(self):
#        with self.assertRaises(ValueError):
#            self.config_helper.verify_integer_exists(self.config_file, 'float_point5')

    def test_int_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(self.config_file, 'int_negative_12', lower_bound=-11)

    def test_int_is_above_lower_bound(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'int_30', lower_bound=29)
        self.assertEquals(30, result)

    def test_int_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(self.config_file, 'int_30', upper_bound=30)

    def test_int_is_below_upper_bound(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'int_1', upper_bound=2)
        self.assertEquals(1, result)

    def test_int_is_within_range(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'int_1', lower_bound=1, upper_bound=2)
        self.assertEquals(1, result)

    def test_float_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(self.config_file, 'float_negative_1point5', lower_bound=1.6)

    def test_float_is_above_lower_bound(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'float_30point5', lower_bound=30.5)
        self.assertEquals(30.5, result)

    def test_float_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(self.config_file, 'float_30point5', upper_bound=30.5)

    def test_float_is_below_upper_bound(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'float_point5', upper_bound=0.6)
        self.assertEquals(0.5, result)

    def test_float_is_within_range(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'float_point5', lower_bound=0.5, upper_bound=0.51)
        self.assertEquals(0.5, result)

    def tearDown(self):
        # Close config file
        pass

if __name__ == '__main__':
    unittest.main()
