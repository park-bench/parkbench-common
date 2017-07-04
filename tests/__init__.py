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
        result = self.config_helper.verify_integer_exists(self.config_file, 'small_int')
        self.assertEqual(result, 1)

    def test_int_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(self.config_file, 'negative_int', lower_bound=0)

    def test_int_is_above_lower_bound(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'very_large_int', lower_bound=20)
        self.assertTrue(result)

    def test_int_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(self.config_file, 'very_large_int', upper_bound=12)

    def test_int_is_below_upper_bound(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'small_int', upper_bound=2)
        self.assertTrue(result)

    def test_int_is_within_range(self):
        result = self.config_helper.verify_integer_within_range(self.config_file, 'small_int', lower_bound=0, upper_bound=5)
        self.assertTrue(result)

    def test_float_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(self.config_file, 'negative_float', lower_bound=3.2)

    def test_float_is_abover_lower_bound(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'very_large_float', lower_bound=1.0)
        self.assertTrue(result)

    def test_float_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(self.config_file, 'very_large_float', upper_bound=3.7)

    def test_float_is_below_upper_bound(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'small_float', upper_bound=3.3)
        self.assertTrue(result)

    def test_float_is_within_range(self):
        result = self.config_helper.verify_number_within_range(self.config_file, 'small_float', lower_bound=-0.1, upper_bound=3.3)
        self.assertTrue(result)

    def tearDown(self):
        # Close config file
        pass

if __name__ == '__main__':
    unittest.main()
