# Copyright 2015 Joel Allen Luellwitz and Andrew Klapp
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

# TODO: A lot of methods are called more thans once. Consider storing the
#   returned value in a variable instead.

import ConfigParser
import logging
import logging.config
import sys

trace_level_number = 5 # debug is 10, error is 20, and so on.


# TODO: All these new methods should have documentation.

# Trace is defined here because being in another class breaks references to self.
def _trace(self, message, *args, **kws):
    if self.isEnabledFor(trace_level_number):
        self._log(trace_level_number, message, args, **kws)

# TODO: This should probably be rewritten eventually to use the typing methods
#   provided in configparser and to just add methods for our specific use cases.
class ConfigHelper():

    def __init__(self):
        # This is one reason why this library is specific to our projects. Our configuration files
        #   currently just have one section.
        self.global_section_name = 'General'
        
        self.option_label = 'Option %s: %s'
        self.option_missing_error_message = 'Option %s not found. Quitting.'
        
        self.logger = logging.getLogger()

    # Returns the file handler for the log file. Mostly used for preserving file
    #   descriptors upon daemonization.
    def get_log_file_handle(self):
        return self.logger.handlers[0].stream.fileno()

    # Applies the configuration defined in _get_logger_config and adds a trace
    #   log level. This should be run as soon as a log file and log level are known.
    def configure_logger(self, log_file, log_level):
        # Make it all uppercase because none of the other config file options
        #   have to be uppercase.
        log_level = log_level.upper()

        # Add a trace method to the Logger class
        logging.addLevelName(trace_level_number, 'TRACE')
        logging.Logger.trace = _trace

        logging_config = self._get_logger_config(log_file, log_level)
        logging.config.dictConfig(logging_config)

    # Verifies an option exists in the application configuration file. This method assumes
    #   a logging file has not been initialized yet.
    # TODO: This method is obsolete now. Figure out whether it can be safely deleted.
    def verify_string_exists_prelogging(self, config_file, option_name):
        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            print(self.option_missing_error_message % option_name)
            sys.exit(1)

        print(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies an option exists in the application configuration file. This method assumes
    #   a logger has been instantiated.
    def verify_string_exists(self, config_file, option_name):
        self.logger.trace('Verifying option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.logger.critical(self.option_missing_error_message % option_name)
            sys.exit(1)

        self.logger.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies a password exists in the application configuration file. This method does not log the
    #   value of the config parameter. This method assumes a logger has been instantiated.
    def verify_password_exists(self, config_file, option_name):
        self.logger.trace('Verifying password %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.logger.critical(self.option_missing_error_message % option_name)
            sys.exit(1)

        self.logger.info('Password %s exists.' % option_name)
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies a numeric option exists in the application configuration file. This method assumes
    #   a logger has been instantiated.
    def verify_number_exists(self, config_file, option_name):
        self.logger.trace('Verifying numeric option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.logger.critical(self.option_missing_error_message % option_name)
            sys.exit(1)

        try:
            float_value = float(config_file.get(self.global_section_name, option_name).strip());
        except ValueError:
            self.logger.critical('Option %s has a value of %s but that is not a number. Quitting.' % \
                (option_name, config_file.get(self.global_section_name, option_name).strip()))
            sys.exit(1)

        self.logger.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return float_value

    # Verifies an integer option exists in the application configuration file. This method assumes
    #   a logger has been instantiated.
    def verify_integer_exists(self, config_file, option_name):
        self.logger.trace('Verifying integer option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.logger.critical(self.option_missing_error_message % option_name)
            sys.exit(1)

        try:
            int_value = int(config_file.get(self.global_section_name, option_name).strip());
        except ValueError:
            self.logger.critical('Option %s has a value of %s but that is not an integer. Quitting.' % \
                (option_name, config_file.get(self.global_section_name, option_name).strip()))
            sys.exit(1)

        self.logger.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return int_value

    # Verifies an option in the application configuration file contains a comma delimited list of numbers.
    #   This method assumes a logger has been instantiated.
    def verify_number_list_exists(self, config_file, option_name):
        self.logger.trace('Verifying numeric list option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.logger.critical(self.option_missing_error_message % option_name)
            sys.exit(1)

        string_array = config_file.get(self.global_section_name, option_name).strip().split(',')
        float_array = [];

        for string_value in string_array:
            try:
                float_value = float(string_value.strip());
            except ValueError:
                self.logger.critical('Option %s has a value of %s but that is not a list of numbers. Quitting.' % \
                    (option_name, config_file.get(self.global_section_name, option_name).strip()))
                sys.exit(1)
            float_array.append(float_value)

        self.logger.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return float_array

    # Just grab a string from the config file.  Don't verify anything, and
    #   return a None object if it is empty or doesn't exist.
    def get_string_if_exists(self, config_file, option_name):
        self.logger.trace('Reading option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            option_text = None
            # return a None object
        else:
            self.logger.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
            option_text = config_file.get(self.global_section_name, option_name).strip()
        return option_text

    # TODO: Look into adding log rotation to our logging config.

    # Returns a dict that defines the logging options we like:
    #   The informative formatter.
    #   A stdout handler.
    #   A file handler.
    def _get_logger_config(self, log_file, log_level):
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
