#!/usr/bin/env python2

# Copyright 2017 Joel Allen Luellwitz and Andrew Klapp
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = 'Joel Luellwitz and Andrew Klapp'
__version__ = '0.8'

import confighelper
import ConfigParser
import logging
import unittest

CONFIG_FILE_PATH = './tests/data/config.txt'


class ConfigValidationTests(unittest.TestCase):
    """To run this test, execute the following from the project root:
    python -m unittest discover --pattern=__init__.py
    """

    def setUp(self):
        # Load config file
        # Pass it to configParser
        self.config_file = ConfigParser.RawConfigParser()
        self.config_file.read(CONFIG_FILE_PATH)

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
    #def test_integer_rejects_float(self):
    #    with self.assertRaises(ValueError):
    #        self.config_helper.verify_integer_exists(self.config_file, 'float_point5')

    def test_int_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(
                self.config_file, 'int_negative_12', lower_bound=-11)

    def test_int_is_above_lower_bound(self):
        result = self.config_helper.verify_integer_within_range(
            self.config_file, 'int_30', lower_bound=30)
        self.assertEquals(30, result)

    def test_int_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_integer_within_range(
                self.config_file, 'int_30', upper_bound=30)

    def test_int_is_below_upper_bound(self):
        result = self.config_helper.verify_integer_within_range(
            self.config_file, 'int_1', upper_bound=2)
        self.assertEquals(1, result)

    def test_int_is_within_range(self):
        result = self.config_helper.verify_integer_within_range(
            self.config_file, 'int_1', lower_bound=1, upper_bound=2)
        self.assertEquals(1, result)

    def test_float_is_below_lower_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(
                self.config_file, 'float_negative_1point5', lower_bound=1.6)

    def test_float_is_above_lower_bound(self):
        result = self.config_helper.verify_number_within_range(
            self.config_file, 'float_30point5', lower_bound=30.5)
        self.assertEquals(30.5, result)

    def test_float_is_above_upper_bound(self):
        with self.assertRaises(ValueError):
            self.config_helper.verify_number_within_range(
                self.config_file, 'float_30point5', upper_bound=30.5)

    def test_float_is_below_upper_bound(self):
        result = self.config_helper.verify_number_within_range(
            self.config_file, 'float_point5', upper_bound=0.6)
        self.assertEquals(0.5, result)

    def test_float_is_within_range(self):
        result = self.config_helper.verify_number_within_range(
            self.config_file, 'float_point5', lower_bound=0.5, upper_bound=0.51)
        self.assertEquals(0.5, result)

if __name__ == '__main__':
    unittest.main()
