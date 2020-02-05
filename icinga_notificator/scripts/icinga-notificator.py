#!/usr/bin/env python3
import argparse
import time
import signal
from elasticsearch import Elasticsearch
from configparser import NoOptionError
import urllib.request
import urllib.parse
import urllib.error

from icinga_notificator.utils import configParser
from icinga_notificator.utils import getUsers
from icinga_notificator.utils import elastic
from icinga_notificator.functions import signals
from icinga_notificator.functions import aggregation
from icinga_notificator.functions import handling
from icinga_notificator.base import consts

####################################
# logging stuff
####################################
import logging
####################################
# main
####################################

if __name__ == "__main__":

    # Default values before parsing
    configFolder = "/etc/icinga-notificator/"
    sleepTimer = 60
    lastCall = dict()
    bkpIcingaUsers = None
    noUsers = True
    logLevel = consts.LOGLEVELS["info"]
    logFile = "/var/log/icinga2/icinga-notificator.log"

    # Parsing arguments
    parser = argparse.ArgumentParser(
        description="Icinga notificator script",
        epilog="Created by Jakub Stollmann <jakub@stlm.cz>",
    )
    parser.add_argument("--debug", help="turn on debug mode", action="store_true")
    parser.add_argument("--logstdout", help="print log also to stdout", action="store_true")
    parser.add_argument("--config", help="specify custom configfile", dest="config")
    parser.add_argument("--cafile", help="specify custom icinga Api CA", dest="cafile")

    args = parser.parse_args()

    if args.config:
        configFolder = args.config

    ###########################################
    # Config file parsing, global variables
    ###########################################

    try:
        config = configParser.ConfigParse(configFolder)

        timePeriod = config.parser._sections["global"]["timeperiod"]
        # WILL EDIT TO ANOTHER SECTION AFTERWARDS
        esIndex = config.parser._sections["global"]["es_index"]
        esQueries = config.parser._sections["queries"]
        icingaApiObj = config.parser._sections["icingaapi"]
        smsEagleObj = config.parser._sections["smseagle"]
        smtpServerHost = config.parser._sections["smtpserver"]["hostname"]
        callModemObj = config.parser._sections["callmodem"]
        slackObj = config.parser._sections["slack"]

    except (NoOptionError, KeyError):
        logging.exception("Error in configuration - check it")
        exit(2)
    except OSError:
        logging.exception("Cannot access configuration - check it")
        exit(2)

    # loglevel from config
    if "logging" in config.parser._sections:
        try:
            logLevel = consts.LOGLEVELS[config.parser._sections["logging"]["level"]]
        except KeyError:
            logLevel = consts.LOGLEVELS["info"]
        exit(2)

    # override config with args
    if args.debug:
        logLevel=consts.LOGLEVELS["debug"]
    if args.cafile:
        icingaApiObj["cafile"] = args.cafile

    ####################
    # Logging INIT
    ####################
    logger = logging.getLogger()
    logger.setLevel(logLevel)

    # set where to log
    if not args.logstdout:
        # create a file handler
        try:
            handlerFILE = logging.FileHandler(logFile)
        except OSError:
            logger.exception("Error in loging init, perhaps problem with file")
        handlerFILE.setLevel(logLevel)
        # create a logging format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s:%(lineno)d  %(message)s")
        handlerFILE.setFormatter(formatter)
        # add handler to logger
        logger.addHandler(handlerFILE)

    logging.getLogger("elasticsearch").setLevel(logLevel+10)
    logging.getLogger("urllib").setLevel(logLevel+10)

    #################
    # Connect to ES
    #################
    try:
        es = Elasticsearch()
    except Exception as e:
        logging.exception("Error creating ES object")
        exit(2)

    ##############################
    # MAIN CYCLE
    ##############################

    while True:
        # User list management
        # Get list, if not possible, wait, tryagain..
        # Use old one if there is no possibility to get new
        for i in range(0, 3):
            icingaUsers = getUsers.getIcingaUsers(icingaApiObj)
            if icingaUsers == 1 or type(icingaUsers) is not dict:
                noUsers = True
                time.sleep(3)
                continue
            else:
                noUsers = False
                bkpIcingaUsers = icingaUsers
                break

        # If we haven't got anything, we cannot continue. Sleep and wait
        if noUsers is True and bkpIcingaUsers is None:
            logging.error("No user database, cannot process notifications")
            time.sleep(30)
            continue
        # If we have backup, we can use it
        if noUsers is True and bkpIcingaUsers is not None:
            icingaUsers = bkpIcingaUsers

        # Set Current time to work with
        workTime = int(round(time.time() * 1000))

        logging.debug("Querying ES, timeperiod: %s, worktime: %s", timePeriod, workTime)
        aggResult = elastic.queryEs(
            es, esIndex, esQueries["agg_notify_per_host"], timePeriod, workTime
        )

        # handle es errors
        if aggResult == 2:
            # Error handling
            logging.error(
                "Error in ES query, sleep and try again...some notifications might go away"
            )
            time.sleep(sleepTimer)
            continue

        # If no notifications, sleep some time, then continue
        if int(aggResult["hits"]["total"]) == 0:
            signal.signal(signal.SIGINT, signals.signalHandler)
            signal.signal(signal.SIGTERM, signals.signalHandler)
            signal.signal(signal.SIGHUP, signals.signalHandler)

            logging.debug("no notifications -> sleeping %d", sleepTimer)
            time.sleep(sleepTimer)
            continue

        # create list of notifications for every contact
        # then iterate and handle for every user
        allNotifications = elastic.queryEs(
            es, esIndex, esQueries["all_unmanaged_notifies"], timePeriod, workTime
        )["hits"]["hits"]

        # handle notification per USER
        # if cannot handle try again, then mark as handled and skip

        userNotifications = aggregation.aggregateBy(allNotifications, "users")

        for user in userNotifications:
            logging.debug("Handling notifications for: %s", user)
            try:
                returnCode = 2
                returnCode, lc = handling.handleNotifications(
                    userNotifications[user],
                    icingaUsers,
                    user,
                    smsEagleObj,
                    smtpServerHost,
                    lastCall,
                    callModemObj,
                    slackObj
                )
                lastCall = lc
            except Exception as e:
                logging.exception("Handle notifications - Exception caught!")

        ret = elastic.markAsHandled(
            es, esIndex, esQueries["update_agg_hosts"], timePeriod, workTime
        )

        if ret == 2:
            logging.error(
                "Failed mark notifications as handled !",
                " Some of them could be send more times",
            )

        # all of these signals will force script to exit
        signal.signal(signal.SIGINT, signals.signalHandler)
        signal.signal(signal.SIGTERM, signals.signalHandler)
        signal.signal(signal.SIGHUP, signals.signalHandler)

        logging.debug("sleeping")
        time.sleep(sleepTimer)
        aggResult = None
