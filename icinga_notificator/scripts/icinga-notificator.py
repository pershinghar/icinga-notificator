#!/usr/bin/env python3
import argparse
import logging
import time
import signal
from elasticsearch import Elasticsearch
from configparser import ConfigParser, NoOptionError, NoSectionError
import urllib.request, urllib.parse, urllib.error

from icinga_notificator.utils import configParser
from icinga_notificator.utils import getUsers
from icinga_notificator.utils import elastic
from icinga_notificator.functions import signals
from icinga_notificator.functions import aggregation
from icinga_notificator.functions import handling


####################################
# main
####################################

if __name__ == "__main__":

    # Default values before parsing
    configFile = "/etc/icinga-notificator.cnf"
    sleepTimer = 60
    lastCall = dict()
    bkpIcingaUsers = None
    noUsers = True

    loggingObj = dict()
    loggingObj["mode"] = logging.INFO
    loggingObj["file"] = "/var/log/icinga2/icinga-notificator.log"

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
        configFile = args.config

    #
    # Config file parsing, global variables
    #

    try:
        config = configParser.ConfigParse(configFile)

        timePeriod = config.parser._sections["global"]["timeperiod"]
        # WILL EDIT TO ANOTHER SECTION AFTERWARDS
        esIndex = config.parser._sections["global"]["es_index"]

        # aggNotifyPerHost
        # allUnmanagedNotifies
        # updateNotifyPerAllHosts

        esQueries = config.parser._sections["queries"]
        icingaApiObj = config.parser._sections["icingaapi"]
        smsEagleObj = config.parser._sections["smseagle"]
        smtpServerHost = config.parser._sections["smtpserver"]["hostname"]
        callModemObj = config.parser._sections["callmodem"]

        if "logging" in config.parser._sections:
            loggingObj.update(config.parser._sections["logging"])

    except NoOptionError as excpt:
        logging.exception("Error in configuration")
        exit(2)

    # override config with args
    if args.debug:
        loggingObj["mode"] = logging.DEBUG

    if args.cafile:
        icingaApiObj["cafile"] = args.cafile

    #
    # Init logging
    #

    logging.basicConfig(
        filename=loggingObj["file"],
        filemode="a",
        format="%(asctime)s - %(levelname)s:%(lineno)d  %(message)s",
        level=loggingObj["mode"],
    )

    if args.logstdout:
        # set up logging to console
        console = logging.StreamHandler()
        console.setLevel(loggingObj["mode"])
        # set a format which is simpler for console use
        formatter = logging.Formatter("%(name)-4s: %(levelname)-8s %(message)s")
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger("").addHandler(console)

    logging.getLogger("elasticsearch").setLevel(logging.WARNING)
    logging.getLogger("urllib").setLevel(logging.WARNING)

    # Connect to ES
    try:
        es = Elasticsearch()
    except Exception as e:
        logging.exception("Error creating ES object")
        exit(2)

    # Active wating with sleep

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
