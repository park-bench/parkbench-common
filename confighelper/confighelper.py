# Copyright 2015-2018 Joel Allen Luellwitz and Andrew Klapp
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

""" confighelper.confighelper helps read and validate options from a ConfigParser object."""

__all__ = ['ConfigHelper', 'ValidationException']
__author__ = 'Joel Luellwitz and Andrew Klapp'
__version__ = '0.8'

import logging
import logging.config
import sys

TRACE_LEVEL_NUMBER = 5  # debug is 10, error is 20, and so on.

OPTION_LABEL = 'Option %s: %s'
OPTION_MISSING_ERROR_MESSAGE = 'Option %s not found.'


def _trace(self, message, *args, **kwargs):
    """Trace is defined here because being in another class breaks references to self.

    message: The messgae to be logged.  Maybe contain placeholders to be populated by args
      and kwargs.
    args: List of positional arguments.
    kwargs: Dictionary of named arguments.
    """
    if self.isEnabledFor(TRACE_LEVEL_NUMBER):
        self._log(TRACE_LEVEL_NUMBER, message, args, **kwargs)


class ValidationException(Exception):
    """Indicates that configuration validation has failed."""


class ConfigHelper(object):
    """Contains methods to help parse and validate ConfigParser configuration files."""

    def __init__(self):
        # This is one reason why this library is specific to our projects.  Our configuration
        #   files currently just have one section.
        self.global_section_name = 'General'

        self.logger = logging.getLogger()

    def get_log_file_handle(self):
        """Returns the file handler for the log file.  Mostly used for preserving file
        descriptors upon daemonization.
        """

        return self.logger.handlers[0].stream.fileno()

    def configure_logger(self, log_file, log_level):
        """Applies the configuration defined in _get_logger_config and adds a trace
        log level.  This should be run as soon as the log level is known.

        log_file: The pathname of the file to log to.
        log_level: Indicates the verbosity of the logging. Valid levels are TRACE, DEBUG,
            INFO, WARNING, ERROR, and CRITICAL.
        """

        # Make it all uppercase because none of the other config file options
        #   have to be uppercase.
        log_level = log_level.upper()

        # Add a trace method to the Logger class
        logging.addLevelName(TRACE_LEVEL_NUMBER, 'TRACE')
        logging.Logger.trace = _trace

        logging_config = self._get_logger_config(log_file, log_level)
        logging.config.dictConfig(logging_config)

    def verify_string_exists(self, config_file, option_name):
        """Verifies an option exists in the application configuration file.  This method
        assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a string.
        """

        self.logger.debug('Verifying option %s.', option_name)
        option_text = self._require_option(config_file, option_name)

        return option_text

    def verify_password_exists(self, config_file, option_name):
        """Verifies a password exists in the application configuration file.  This method
        does not log the value of the config parameter.  This method assumes a logger has
        been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a string.
        """
        self.logger.debug('Verifying password %s.', option_name)

        option_value = None
        if config_file.has_option(self.global_section_name, option_name):
            option_value = config_file.get(self.global_section_name, option_name)

        if option_value == '':
            option_value = None

        if option_value is None:
            message = OPTION_MISSING_ERROR_MESSAGE % option_name
            self.logger.error(message)

        self.logger.info('Password %s exists.', option_name)
        return option_value

    def verify_number_exists(self, config_file, option_name):
        """Verifies a numeric option exists in the application configuration file.  This
        method assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a number.
        """

        self.logger.debug('Verifying numeric option %s.', option_name)
        option_text = self._require_option(config_file, option_name)

        try:
            float_value = float(option_text)
        except ValueError:
            message = 'Option %s has a value of %s but that is not a number.' % (
                option_name, option_text)
            self.logger.error(message)
            raise ValidationException(message)

        return float_value

    def verify_integer_exists(self, config_file, option_name):
        """Verifies an integer option exists in the application configuration file.  This
        method assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a number.
        """

        self.logger.debug('Verifying integer option %s.', option_name)
        option_text = self._require_option(config_file, option_name)

        try:
            int_value = int(option_text)
        except ValueError:
            message = \
                'Option %s has a value of %s, but that is not an integer.' % \
                (option_name, option_text)
            self.logger.error(message)
            raise ValidationException(message)

        return int_value

    def verify_number_within_range(
            self, config_file, option_name, lower_bound=None, upper_bound=None):
        """Verifies a numeric option exists in the application configuration file and is
        below the upper bound and above or equal to the lower bound.  This method assumes a
        logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        lower_bound: The quantity the value should not be less than.
        upper_bound: The quantity the value should not be equal to or greater than.
        Returns the option value as a number.
        """

        float_value = self.verify_number_exists(config_file, option_name)
        self._boundary_check(float_value, upper_bound=upper_bound, lower_bound=lower_bound)
        return float_value

    def verify_integer_within_range(
            self, config_file, option_name, lower_bound=None, upper_bound=None):
        """Verifies an integer option exists in the application configuration file and is
        below the upper bound and above or equale to the lower bound.  This method assumes a
        logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        lower_bound: The quantity the value should not be less than.
        upper_bound: The quantity the value should not be equal to or greater than.
        Returns the option value as a number.
        """

        int_value = self.verify_integer_exists(config_file, option_name)
        self._boundary_check(int_value, upper_bound=upper_bound, lower_bound=lower_bound)
        return int_value

    def _boundary_check(self, value, lower_bound, upper_bound):
        """Checks that the value is above or equal to the lower_bound and below the
        upper_bound and raises a ValidationException if it is not.

        value: The numeric value being validated.
        lower_bound: The quantity the value should not be less than.
        upper_bound: The quantity the value should not be equal to or greater than.
        """
        self.logger.debug('Checking boundaries.')

        if lower_bound is not None:
            if value < lower_bound:
                message = 'Option has a value of %s, which is below lower boundary %s.' % (
                    value, lower_bound)
                raise ValidationException(message)

        if upper_bound is not None:
            if value >= upper_bound:
                message = 'Option has a value of %s, which is equal to or above upper ' \
                          'boundary %s.' % (value, upper_bound)
                raise ValidationException(message)

    def verify_valid_integer_in_list(self, config_file, option_name, valid_options):
        """Verifies an integer option is valid given a list of acceptable options.  This
        method assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        valid_options: A container of acceptable numeric values.
        Returns the option value as a number.
        """

        self.logger.debug('Verifying integer option %s.', option_name)
        int_value = self.verify_integer_exists(config_file, option_name)

        if int_value not in valid_options:
            message = '%s is not a valid value for %s.' % (int_value, option_name)
            self.logger.error(message)
            raise ValidationException(message)

        return int_value

    def verify_number_list_exists(self, config_file, option_name):
        """Verifies an option in the application configuration file contains a comma
        delimited list of numbers.  This method assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as an array of numbers.
        """

        self.logger.debug('Verifying numeric list option %s.', option_name)
        option_text = self._require_option(config_file, option_name)

        string_array = option_text.split(',')
        float_array = []

        for string_value in string_array:
            try:
                float_value = float(string_value.strip())
            except ValueError:
                message = 'Option %s has a value of %s but that is not a list of numbers. ' \
                    % (option_name, option_text)
                self.logger.error(message)
                raise ValidationException(message)
            float_array.append(float_value)

        return float_array

    def verify_string_list_exists(self, config_file, option_name):
        """Parses a comma-delimited list of strings into an actual list and strips
        leading and trailing whitespace.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as an array of strings.
        """
        option_text = self.verify_string_exists(config_file, option_name)
        raw_strings = option_text.split(',')

        # run strip() on each item in raw_string_array
        trimmed_strings = [string.strip() for string in raw_strings]
        return trimmed_strings

    def verify_boolean_exists(self, config_file, option_name):
        """Verifies a boolean option exists in the application configuration file.  This
        method assumes a logger has been instantiated.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a boolean.
        """
        option_text = self._require_option(config_file, option_name).lower()
        if option_text == 'true':
            boolean_value = True
        elif option_text == 'false':
            boolean_value = False
        else:
            message = 'Option %s is not "true" or "false".' % option_name
            self.logger.error(message)
            raise ValidationException(message)

        return boolean_value

    def get_string_if_exists(self, config_file, option_name):
        """Just grab a string from the config file.  Don't verify anything, and
        return a None object if it is empty or doesn't exist.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a string or None if the option value does not exist.
        """

        self.logger.debug('Reading option %s.', option_name)
        option_value = self._get_option(config_file, option_name)

        return option_value

    def _require_option(self, config_file, option_name):
        """Retrieves the requested option from the ConfigParser instance and throws a
        ValidationException if the option does not exist.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a string.
        """
        option_value = self._get_option(config_file, option_name)

        if option_value is None:
            message = OPTION_MISSING_ERROR_MESSAGE % option_name
            self.logger.error(message)
            raise ValidationException(message)

        return option_value

    def _get_option(self, config_file, option_name):
        """Retrieves the requested option from the ConfigParser instance.

        config_file: The ConfigParser instance.
        option_name: The name of the option being retrieved.
        Returns the option value as a string or None if the option value does not exist.
        """
        option_value = None
        if config_file.has_option(self.global_section_name, option_name):
            option_value = config_file.get(self.global_section_name, option_name)

        if option_value == '':
            option_value = None

        if option_value:
            self.logger.info(OPTION_LABEL, option_name, option_value)

        return option_value

    # TODO: Eventually, look into adding log rotation to our logging config. (issue 4)
    def _get_logger_config(self, log_file, log_level):
        """Returns a dict that defines the logging options we like:
        The informative formatter.
        A stdout handler.
        A file handler.
        """

        logger_config = {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default',
                    'stream': sys.stdout,
                    'level': log_level
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'formatter': 'default',
                    'filename': log_file,
                    'level': log_level
                }
            },
            'loggers': {
                '': {
                    'handlers': ['file', 'console'],
                    'level': log_level
                }
            }
        }
        return logger_config
