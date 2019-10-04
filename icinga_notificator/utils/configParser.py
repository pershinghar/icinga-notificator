#!/usr/bin/env/python3
# ConfigParser manager class ->
# original author: Robert Vojcik (robert.vojcik@livesport.eu)
# forked edit: Jakub Stollmann (jakub@stlm.cz)

from configparser import ConfigParser
import logging


class ConfigParse:
    """
    This Class automaticly check for config file and parse it.
    Creates variables structure to be able access it

    It Also had config reload feature

    Config file format:

    [selector]
    parameter1=value
    parameter2=value
    ...

    Class provide basic manipulation with config file.
    More information about manipulation can be find in ConfigParser
    official documentation.

    Can access ConfigParser directly ConfigParse.parser.[.....]

    """

    def config_open(self):
        """ Open Config File """
        try:
            self.cfd = open(self.cf)
        except IOError as e:
            logging.exception("Unable to load config file")
            return 2

    def config_close(self):
        """ Close config file descriptor """
        self.cfd.close()

    def __init__(self, config_file):
        """ Initialize class, load config file """
        # Config File Descriptor
        self.cfd = False
        self.cf = config_file
        self.parser = False

        self.config_open()
        self.config_parse()
        self.config_close()

    def config_parse(self):
        """ Parse config file """

        self.parser = ConfigParser()
        self.parser.readfp(self.cfd)

    def config_reload(self):
        """ Reload configuration file """
        self.__init__(self.cf)
