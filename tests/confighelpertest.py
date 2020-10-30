#!/usr/bin/env python2

# Copyright 2017-2020 Joel Allen Luellwitz and Emily Frost
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

"""Tests the ConfigHelper class."""

__author__ = 'Joel Luellwitz and Emily Frost'
__version__ = '0.8'

import configparser
import logging
from parkbenchcommon import confighelper
from parkbenchcommon.confighelper import ValidationException
import unittest
from unittest.mock import call
from unittest.mock import MagicMock

CONFIG_FILE_PATH = './tests/data/config.txt'


class ConfigHelperTest(unittest.TestCase):
    "Tests the ConfigHelper class."

    def setUp(self):
        # Load config file
        # Pass it to configParser
        self.config_file = configparser.RawConfigParser()
        self.config_file.read(CONFIG_FILE_PATH)

        self.logger = MagicMock()
        logging.getLogger = MagicMock(return_value=self.logger)

        log_file = '/dev/null'
        log_level = 'trace'
        self.config_helper = confighelper.ConfigHelper()
        self.config_helper.configure_logger(log_file, log_level)

    def test_get_log_file_handle_code_coverage(self):
        result = self.config_helper.get_log_file_handle()

    def test_verify_string_exists_when_string_exists(self):
        name = 'verify-string-exists'
        value = 'Of course I exist!'

        result = self.config_helper.verify_string_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, value)

    def test_verify_string_exists_when_blank(self):
        name = 'verify-string-exists-blank'
        not_found_message = 'Option verify-string-exists-blank not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_string_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_string_exists_when_no_string_exists(self):
        name = 'verify-no-string-exists'
        not_found_message = 'Option verify-no-string-exists not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_string_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_password_exists_when_password_exists(self):
        name = 'verify-password-exists'
        value = 'r00t'

        result = self.config_helper.verify_password_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying password %s.', name)
        self.logger.info.assert_called_with('Password %s exists.', name)

    def test_verify_password_exists_when_password_is_blank(self):
        name = 'verify-password-exists-blank'
        not_found_message = 'Option verify-password-exists-blank not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_password_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying password %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_password_exists_when_option_name_is_missing(self):
        name = 'verify-password-exists-name-missing'
        not_found_message = 'Option verify-password-exists-name-missing not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_password_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying password %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_number_exists_when_number_exists(self):
        name = 'verify-number-exists'
        value = 3.3

        result = self.config_helper.verify_number_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying numeric option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.3')

    def test_verify_number_exists_when_no_value_exists(self):
        name = 'verify-no-number-exists'
        not_found_message = 'Option verify-no-number-exists not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_number_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_number_exists_when_not_a_number(self):
        name = 'verify-number-exists-not-number'
        not_valid_message = 'Option verify-number-exists-not-number has a value of l337 ' \
            'but that is not a number.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_number_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_integer_exists_when_integer_exists(self):
        name = 'verify-integer-exists'
        value = 3

        result = self.config_helper.verify_integer_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_exists_when_no_value_exists(self):
        name = 'verify-no-integer-exists'
        not_found_message = 'Option verify-no-integer-exists not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_integer_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_integer_exists_when_not_an_integer(self):
        name = 'verify-integer-exists-not-integer'
        not_valid_message = 'Option verify-integer-exists-not-integer has a value of 3.3 ' \
            'but that is not an integer.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_integer_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_number_within_range_when_number_below_lower_bound(self):
        name = 'verify-number-within-range-range-edge'
        value = 3.899999
        below_bounds_message = 'Option has a value of 3.899999, which is below lower ' \
            'boundary 3.9.'

        with self.assertRaisesRegex(ValidationException, below_bounds_message):
            self.config_helper.verify_number_within_range(
                self.config_file, name, lower_bound=3.9)

        expected_debug_calls = [
            call('Verifying numeric option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.899999')

    def test_verify_number_within_range_when_number_equal_to_lower_bound(self):
        name = 'verify-number-within-range'
        value = 3.3

        result = self.config_helper.verify_number_within_range(
            self.config_file, name, lower_bound=3.3)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying numeric option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.3')

    def test_verify_number_within_range_when_number_within_range(self):
        name = 'verify-number-within-range'
        value = 3.3

        result = self.config_helper.verify_number_within_range(
            self.config_file, name, lower_bound=3.1, upper_bound=4.1)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying numeric option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.3')

    def test_verify_number_within_range_when_number_below_upper_bound(self):
        name = 'verify-number-within-range-range-edge'
        value = 3.899999

        result = self.config_helper.verify_number_within_range(
            self.config_file, name, upper_bound=3.9)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying numeric option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.899999')

    def test_verify_number_within_range_when_number_equal_to_upper_bound(self):
        name = 'verify-number-within-range'
        value = 3.3
        above_bounds_message = 'Option has a value of 3.3, which is equal to or above ' \
            'upper boundary 3.3.'

        with self.assertRaisesRegex(ValidationException, above_bounds_message):
            self.config_helper.verify_number_within_range(
                self.config_file, name, upper_bound=3.3)

        expected_debug_calls = [
            call('Verifying numeric option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3.3')

    def test_verify_number_within_range_when_no_value_exists(self):
        name = 'verify-number-within-range-no-value'
        not_found_message = 'Option verify-number-within-range-no-value not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_number_within_range(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_number_within_range_when_not_a_number(self):
        name = 'verify-number-within-range-not-number'
        not_valid_message = 'Option verify-number-within-range-not-number has a value of l337 ' \
            'but that is not a number.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_number_within_range(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_integer_within_range_when_integer_below_lower_bound(self):
        name = 'verify-integer-within-range'
        value = 3
        below_bounds_message = 'Option has a value of 3, which is below lower boundary 4.'

        with self.assertRaisesRegex(ValidationException, below_bounds_message):
            self.config_helper.verify_integer_within_range(
                self.config_file, name, lower_bound=4)

        expected_debug_calls = [
            call('Verifying integer option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_within_range_when_integer_equal_to_lower_bound(self):
        name = 'verify-integer-within-range'
        value = 3

        result = self.config_helper.verify_integer_within_range(
            self.config_file, name, lower_bound=3)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying integer option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_within_range_when_integer_within_range(self):
        name = 'verify-integer-within-range'
        value = 3

        result = self.config_helper.verify_integer_within_range(
            self.config_file, name, lower_bound=1, upper_bound=5)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying integer option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_within_range_when_integer_below_upper_bound(self):
        name = 'verify-integer-within-range'
        value = 3

        result = self.config_helper.verify_integer_within_range(
            self.config_file, name, upper_bound=4)

        self.assertEqual(value, result)
        expected_debug_calls = [
            call('Verifying integer option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_within_range_when_integer_equal_to_upper_bound(self):
        name = 'verify-integer-within-range'
        value = 3.3
        above_bounds_message = 'Option has a value of 3, which is equal to or above ' \
            'upper boundary 3.'

        with self.assertRaisesRegex(ValidationException, above_bounds_message):
            self.config_helper.verify_integer_within_range(
                self.config_file, name, upper_bound=3)

        expected_debug_calls = [
            call('Verifying integer option %s.', name), call('Checking boundaries.')]
        self.logger.debug.assert_has_calls(expected_debug_calls)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_integer_within_range_when_no_value_exists(self):
        name = 'verify-integer-within-range-no-value'
        not_found_message = 'Option verify-integer-within-range-no-value not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_integer_within_range(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_integer_within_range_when_not_a_integer(self):
        name = 'verify-integer-within-range-not-number'
        not_valid_message = 'Option verify-integer-within-range-not-integer has a value ' \
            'of l337 but that is not an integer.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_integer_within_range(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_integer_within_range_when_not_a_integer(self):
        name = 'verify-integer-within-range-not-integer'
        not_valid_message = 'Option verify-integer-within-range-not-integer has a value ' \
            'of 3.3 but that is not an integer.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_integer_within_range(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_valid_integer_in_list_when_value_exists_in_list(self):
        name = 'verify-valid-integer-in-list'

        result = self.config_helper.verify_valid_integer_in_list(
            self.config_file, name, [1, 3, 5])

        self.assertEqual(3, result)
        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_valid_integer_in_list_when_no_value_exists(self):
        name = 'verify-valid-integer-in-list-no-value'
        not_found_message = 'Option verify-valid-integer-in-list-no-value not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_valid_integer_in_list(
                self.config_file, name, [1, 3, 5])

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_valid_integer_in_list_when_not_an_integer(self):
        name = 'verify-valid-integer-in-list-not-integer'
        not_valid_message = 'Option verify-valid-integer-in-list-not-integer has a value ' \
            'of 3.3 but that is not an integer.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_valid_integer_in_list(
                self.config_file, name, [1, 3, 5])

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_valid_integer_in_list_when_value_absent_from_list(self):
        name = 'verify-valid-integer-in-list'
        not_valid_message = '3 is not a valid value for verify-valid-integer-in-list.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_valid_integer_in_list(
                self.config_file, name, [0, 2, 4, 6])

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_valid_integer_in_list_when_empty_list(self):
        name = 'verify-valid-integer-in-list'
        not_valid_message = '3 is not a valid value for verify-valid-integer-in-list.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_valid_integer_in_list(
                self.config_file, name, [])

        self.logger.debug.assert_called_with('Verifying integer option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '3')

    def test_verify_number_list_exists_when_valid_list_exists(self):
        name = 'verify-number-list-exists'
        value = [-3, 239, 5]

        result = self.config_helper.verify_number_list_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying numeric list option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '-3,239,5')

    def test_verify_number_list_exists_when_no_value_exists(self):
        name = 'verify-number-list-exists-no-value'
        not_found_message = 'Option verify-number-list-exists-no-value not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_number_list_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric list option %s.', name)
        self.logger.error.assert_called_with(not_found_message)

    def test_verify_number_list_exists_when_not_a_number_list(self):
        name = 'verify-number-list-exists-not-number-list'
        not_valid_message = 'Option verify-number-list-exists-not-number-list has a value ' \
            'of -3,text,5 but that is not a list of numbers.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_number_list_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying numeric list option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_number_list_exists_when_list_of_one(self):
        name = 'verify-number-list-exists-one-number'
        value = [-3]

        result = self.config_helper.verify_number_list_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying numeric list option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '-3')

    def test_get_string_list_if_exists_when_valid_list_exists(self):
        name = 'get-string-list-if-exists'
        value = ['-3', 'text', '239']

        result = self.config_helper.get_string_list_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '-3,text,239')

    def test_get_string_list_if_exists_when_no_value_exists(self):
        name = 'get-string-list-if-exists-no-value'
        value = []

        result = self.config_helper.get_string_list_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)

    def test_get_string_list_if_exists_when_list_of_one(self):
        name = 'get-string-list-if-exists-one-string'
        value = ['text']

        result = self.config_helper.get_string_list_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, 'text')

    def test_verify_string_list_exists_when_valid_list_exists(self):
        name = 'verify-string-list-exists'
        value = ['-3', 'text', '239']

        result = self.config_helper.verify_string_list_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, '-3,text,239')

    def test_verify_string_list_exists_when_no_value_exists(self):
        name = 'verify-string-list-exists-no-value'
        not_valid_message = 'Option verify-string-list-exists-no-value not found.'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_string_list_exists(self.config_file, name)

        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.error.assert_called_with(not_valid_message)

    def test_verify_string_list_exists_when_list_of_one(self):
        name = 'verify-string-list-exists-one-string'
        value = ['text']

        result = self.config_helper.verify_string_list_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Verifying option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, 'text')

    def test_verify_boolean_exists_when_true(self):
        name = 'verify-boolean-exists-true'
        value = 'true'

        result = self.config_helper.verify_boolean_exists(self.config_file, name)

        self.assertEqual(True, result)
        self.logger.info.assert_called_with('Option %s: %s', name, value)

    def test_verify_boolean_exists_when_uppercase_true(self):
        name = 'verify-boolean-exists-true-uppercase'
        value = 'TRUE'

        result = self.config_helper.verify_boolean_exists(self.config_file, name)

        self.assertEqual(True, result)
        self.logger.info.assert_called_with('Option %s: %s', name, value)

    def test_verify_boolean_exists_when_false(self):
        name = 'verify-boolean-exists-false'
        value = 'false'

        result = self.config_helper.verify_boolean_exists(self.config_file, name)

        self.assertEqual(False, result)
        self.logger.info.assert_called_with('Option %s: %s', name, value)

    def test_verify_boolean_exists_when_no_value_exists(self):
        name = 'verify-no-boolean-exists'
        not_found_message = 'Option verify-no-boolean-exists not found.'

        with self.assertRaisesRegex(ValidationException, not_found_message):
            self.config_helper.verify_boolean_exists(self.config_file, name)

        self.logger.error.assert_called_with(not_found_message)

    def test_verify_boolean_exists_when_not_a_boolean(self):
        name = 'verify-boolean-exists-invalid'
        not_valid_message = 'Option verify-boolean-exists-invalid is not "true" or ' \
            '"false".'

        with self.assertRaisesRegex(ValidationException, not_valid_message):
            self.config_helper.verify_boolean_exists(self.config_file, name)

        self.logger.error.assert_called_with(not_valid_message)

    def test_get_string_if_exists_when_string_exists(self):
        name = 'get-string-if-exists'
        value = 'I exist!'

        result = self.config_helper.get_string_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)
        self.logger.info.assert_called_with('Option %s: %s', name, value)

    def test_get_string_if_exists_when_blank(self):
        name = 'get-string-if-exists-blank'
        value = None

        result = self.config_helper.get_string_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)

    def test_get_string_if_exists_when_missing(self):
        name = 'get-string-if-exists-missing'
        value = None

        result = self.config_helper.get_string_if_exists(self.config_file, name)

        self.assertEqual(value, result)
        self.logger.debug.assert_called_with('Reading option %s.', name)
