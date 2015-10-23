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
import timber
import sys

class ConfigHelper():

    def __init__(self):
        # This is one reason why this library is specific to our projects. Our configuration files
        #   currently just have one section.
        self.global_section_name = 'General'
        
        self.option_label = 'Option %s: %s'
        self.option_missing_error_message = 'Option %s not found. Quitting.'
        self.timber = None

    # Verifies an option exists in the application configuration file. This method assumes
    #   a logging file has not been initialized yet.
    def verify_string_exists_prelogging(self, config_file, option_name):
        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            print(self.option_missing_error_message % option_name)
            sys.exit(1)

        print(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies an option exists in the application configuration file. This method assumes
    #   a Timber instance has been created.
    def verify_string_exists(self, config_file, option_name):
        self._init_timber_if_none()

        self.timber.trace('Verifying option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.timber.fatal(self.option_missing_error_message % option_name)
            sys.exit(1)

        self.timber.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies a password exists in the application configuration file. This method does not log the
    #   value of the config parameter. This method assumes a Timber instance has been created.
    def verify_password_exists(self, config_file, option_name):
        self._init_timber_if_none()

        self.timber.trace('Verifying password %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.timber.fatal(self.option_missing_error_message % option_name)
            sys.exit(1)

        self.timber.info('Password %s exists.' % option_name)
        return config_file.get(self.global_section_name, option_name).strip()

    # Verifies a numeric option exists in the application configuration file. This method assumes
    #   a Timber instance has been created.
    def verify_number_exists(self, config_file, option_name):
        self._init_timber_if_none()

        self.timber.trace('Verifying numeric option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.timber.fatal(self.option_missing_error_message % option_name)
            sys.exit(1)

        try:
            float_value = float(config_file.get(self.global_section_name, option_name).strip());
        except ValueError:
            self.timber.fatal('Option %s has a value of %s but that is not a number. Quitting.' % \
                (option_name, config_file.get(self.global_section_name, option_name).strip()))
            sys.exit(1)

        self.timber.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return float_value

    # Verifies an integer option exists in the application configuration file. This method assumes
    #   a Timber instance has been created.
    def verify_integer_exists(self, config_file, option_name):
        self._init_timber_if_none()

        self.timber.trace('Verifying integer option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.timber.fatal(self.option_missing_error_message % option_name)
            sys.exit(1)

        try:
            int_value = int(config_file.get(self.global_section_name, option_name).strip());
        except ValueError:
            self.timber.fatal('Option %s has a value of %s but that is not an integer. Quitting.' % \
                (option_name, config_file.get(self.global_section_name, option_name).strip()))
            sys.exit(1)

        self.timber.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return int_value

    # Verifies an option in the application configuration file contains a comma delimited list of numbers.
    #   This method assumes a Timber instance has been created.
    def verify_number_list_exists(self, config_file, option_name):
        self._init_timber_if_none()

        self.timber.trace('Verifying numeric list option %s' % option_name)

        if (not(config_file.has_option(self.global_section_name, option_name)) or \
                (config_file.get(self.global_section_name, option_name).strip() == '')):
            self.timber.fatal(self.option_missing_error_message % option_name)
            sys.exit(1)

        string_array = config_file.get(self.global_section_name, option_name).strip().split(',')
        float_array = [];

        for string_value in string_array:
            try:
                float_value = float(string_value.strip());
            except ValueError:
                self.timber.fatal('Option %s has a value of %s but that is not a list of numbers. Quitting.' % \
                    (option_name, config_file.get(self.global_section_name, option_name).strip()))
                sys.exit(1)
            float_array.append(float_value)

        self.timber.info(self.option_label % (option_name, config_file.get(self.global_section_name, option_name)))
        return float_array
    
    # Find the existing Timber instance which should have been created by the parent process.
    def _init_timber_if_none(self):
        if (self.timber == None):
            self.timber = timber.get_instance()

