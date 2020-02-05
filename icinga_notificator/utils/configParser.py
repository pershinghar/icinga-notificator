#!/usr/bin/env/python3
# ConfigParser manager class ->
# original author: Robert Vojcik (robert.vojcik@livesport.eu)
# forked edit: Jakub Stollmann (jakub@stlm.cz)

from configparser import ConfigParser
import logging
import os


class ConfigParse:
    """
    This Class automaticly check for config file and parse it.
    If it's directory, it will include all *.conf files in it.
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

    def __init__(self, config_file):
        """ Initialize class, load config file """
        self.parser = False
        fileList = list()

        if os.path.isfile(config_file):
            fileList.append(self.config_open(config_file))
        elif os.path.isdir(config_file):
            for file in os.listdir(config_file):
                if file.endswith(".conf") or file.endswith(".cnf"):
                    fileList.append(config_file + '/' + file)
        else:
            raise OSError(2, "No config found", fileList)

        if len(fileList) == 0:
            raise OSError(2, "No config found", fileList)

        ret = self.config_parse(fileList)
        logging.debug(ret)

        return(None)

    def config_parse(self, fileList):
        """ Parse config file """
        self.parser = ConfigParser()
        return(self.parser.read(fileList))

    def config_reload(self, config_file):
        """ Reload configuration file """
        self.__init__(config_file)
        return
