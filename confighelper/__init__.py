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

# TODO #5: Most methods read values more than once. Store those in a method-level variable.
# TODO #6: Write a method to abstract error cases for retreiving variables from the 

__all__ = ['ValidationException', 'ConfigHelper']
__author__ = 'Joel Luellwitz and Andrew Klapp'
__version__ = '0.8'

import logging
import logging.config
import sys

TRACE_LEVEL_NUMBER = 5  # debug is 10, error is 20, and so on.


def _trace(self, message, *args, **kws):
    """Trace is defined here because being in another class breaks references to self."""
    if self.isEnabledFor(TRACE_LEVEL_NUMBER):
        self._log(TRACE_LEVEL_NUMBER, message, args, **kws)


class ValidationException(Exception):
    """Indicates that configuration validation has failed."""


# TODO #3: Add a method to get a list of strings.
# TODO #7: Eventually, this should probably be rewritten eventually to use the typing methods
#   provided in configparser and to just add methods for our specific use cases.
class ConfigHelper():
    """Contains many methods to help with configuration."""

    def __init__(self):
        # This is one reason why this library is specific to our projects.  Our configuration
        #   files currently just have one section.
        self.global_section_name = 'General'

        self.option_label = 'Option %s: %s'
        self.option_missing_error_message = 'Option %s not found.'

        self.logger = logging.getLogger()

    def get_log_file_handle(self):
        """Returns the file handler for the log file.  Mostly used for preserving file
        descriptors upon daemonization.
        """

        return self.logger.handlers[0].stream.fileno()

    def configure_logger(self, log_file, log_level):
        """Applies the configuration defined in _get_logger_config and adds a trace
        log level.  This should be run as soon as a log file and log level are known.
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
        """

        self.logger.debug('Verifying option %s', option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        self.logger.info(self.option_label, option_name, config_file.get(
            self.global_section_name, option_name))
        return config_file.get(self.global_section_name, option_name).strip()

    def verify_password_exists(self, config_file, option_name):
        """Verifies a password exists in the application configuration file.  This method
        does not log the value of the config parameter.  This method assumes a logger has
        been instantiated.
        """

        self.logger.debug('Verifying password %s', option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        self.logger.info('Password %s exists.', option_name)
        return config_file.get(self.global_section_name, option_name).strip()

    def verify_number_exists(self, config_file, option_name):
        """Verifies a numeric option exists in the application configuration file.  This
        method assumes a logger has been instantiated.
        """

        self.logger.debug('Verifying numeric option %s', option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        try:
            float_value = float(
                config_file.get(self.global_section_name, option_name).strip())
        except ValueError:
            message = 'Option %s has a value of %s but that is not a number.' % (
                option_name, config_file.get(self.global_section_name, option_name).strip())
            self.logger.critical(message)
            raise ValidationException(message)

        self.logger.info(self.option_label, option_name, config_file.get(
            self.global_section_name, option_name))
        return float_value

    def verify_integer_exists(self, config_file, option_name):
        """Verifies an integer option exists in the application configuration file.  This
        method assumes a logger has been instantiated.
        """

        self.logger.debug('Verifying integer option %s', option_name)
        option_text = self._get_option(config_file, option_name)

        if option_text is None:
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        try:
            int_value = int(option_text)
        except ValueError:
            message = \
                'Option %s has a value of %s, but that is not an integer.' % \
                (option_name, option_text)
            self.logger.critical(message)
            raise ValidationException(message)

        self.logger.info(self.option_label, option_name, option_text)
        return int_value

    def verify_number_within_range(
            self, config_file, option_name, upper_bound=None, lower_bound=None):
        """Verifies a numeric option exists in the application configuration file and is
        below the upper bound and above or equal to the lower bound.  This method assumes a
        logger has been instantiated.
        """

        float_value = self.verify_number_exists(config_file, option_name)
        self._boundary_check(float_value, upper_bound=upper_bound, lower_bound=lower_bound)
        return float_value

    def verify_integer_within_range(
            self, config_file, option_name, upper_bound=None, lower_bound=None):
        """Verifies an integer option exists in the application configuration file and is
        below the upper bound and above or equale to the lower bound.  This method assumes a
        logger has been instantiated.
        """

        int_value = self.verify_integer_exists(config_file, option_name)
        self._boundary_check(int_value, upper_bound=upper_bound, lower_bound=lower_bound)
        return int_value

    def _boundary_check(self, value, upper_bound, lower_bound):
        """Check that value is below upper_bound and above lower_bound, and raises
        a ValueError exception if they are not.
        """

        self.logger.debug('Checking boundaries.')

        if upper_bound is not None:
            if value >= upper_bound:
                message = 'Option has a value of %s, which is above upper boundary %s.' % (
                    value, upper_bound)
                raise ValidationException(message)

        if lower_bound is not None:
            if value < lower_bound:
                message = 'Option has a value of %s, which is below lower boundary %s.' % (
                    value, lower_bound)
                raise ValidationException(message)

    def verify_valid_integer_in_list(self, config_file, option_name, valid_options):
        """Verifies an integer option is valid given a list of acceptable options.  This
        method assumes a logger has been instantiated.
        """

        self.logger.debug('Verifying integer option %s', option_name)
        int_value = self.verify_integer_exists(config_file, option_name)

        if int_value not in valid_options:
            message = '%s is not a valid value for %s.' % (int_value, option_name)
            self.logger.critical(message)
            raise ValidationException(message)

        return int_value

    def verify_number_list_exists(self, config_file, option_name):
        """Verifies an option in the application configuration file contains a comma
        delimited list of numbers.  This method assumes a logger has been instantiated.
        """

        self.logger.debug('Verifying numeric list option %s', option_name)
        option_text = self._get_option(config_file, option_name)

        if option_text is None:
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        string_array = option_text.split(',')
        float_array = []

        for string_value in string_array:
            try:
                float_value = float(string_value.strip())
            except ValueError:
                message = 'Option %s has a value of %s but that is not a list of numbers. ' \
                    % (option_name, option_text)
                self.logger.critical(message)
                raise ValidationException(message)
            float_array.append(float_value)

        self.logger.info(self.option_label, option_name, option_text)
        return float_array

    def get_string_if_exists(self, config_file, option_name):
        """Just grab a string from the config file.  Don't verify anything, and
        return a None object if it is empty or doesn't exist.
        """

        self.logger.debug('Reading option %s', option_name)
        option_text = self._get_option(config_file, option_name)

        if option_text:
            self.logger.info(self.option_label, option_name, option_text)

    def _get_option(self, config_file, option_name):
        """Reads an option named option_name from config_file."""
        option_value = None
        if config_file.has_option(self.global_section_name, option_name):
            option_value = config_file.get(self.global_section_name, option_name).strip()

        if option_value == '':
            option_value = None

        return option_value

    def _require_option(self, config_file, option_name):
        option_value = self._get_option(config_file, option_name)

        if option_value is None:
            message = self.option_missing_error_message % option_name
            self.logger.critical(message)
            raise ValidationException(message)

        return option_value

    # TODO #4: Eventually, look into adding log rotation to our logging config.
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
