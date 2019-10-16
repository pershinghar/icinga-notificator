#!/usr/bin/env/python3
#
# Notification handling (sending)
#

import logging
from icinga_notificator.classes import icingaNotification as icn
from icinga_notificator.functions import parsing
from icinga_notificator.functions import sending


def handleNotifications(
    notificationsToHandle,
    icingaUsers,
    user,
    smsModem,
    smtpServerHost,
    lastCall,
    callModemObj,
):
    """ Function which takes notifications, parses them and then send them to all of coresponding users """
    if (
        (user is None)
        or (user.lower() not in icingaUsers is None)
        or ("vars" not in icingaUsers[user.lower()])
        or (icingaUsers[user.lower()] is None)
        or ("notification_options" not in icingaUsers[user.lower()]["vars"])
        or (icingaUsers[user.lower()]["vars"]["notification_options"] is None)
    ):
        try:
            if icingaUsers[user.lower()]["vars"]["ignore_notificator"] is True:
                logging.debug("Not handling notifications for user %s", user)
            else:
                logging.info("Cannot handle notifications, something is wrong for this user..")
        except KeyError:
            logging.info("Cannot handle notifications, something is wrong for this user..")
        finally:
            return (1, lastCall)

    options = icingaUsers[user.lower()]["vars"]["notification_options"]

    # Init some things
    send = False
    ret = -1
    # Iterrate over sending types to correctly filter this shit.
    for nType, states in options.items():
        if ret == -1:
            ret = 0

        message = ""
        notificationsList = list()

        # Iterate and filter notifications, fill list
        for notification in notificationsToHandle:
            icingaNotifObj = icn.icingaNotification(notification, user)

            # manage OK notification - based on previous state
            # if last state is defined in user options, then move ahead
            logging.debug("Notification:")
            logging.debug("\t state: %s", icingaNotifObj.notificationState.lower())
            logging.debug(
                "\t stateBefore: %s", icingaNotifObj.notificationStateBefore.lower()
            )
            logging.debug("User:")
            logging.debug("\t %s : %s", nType, states)

            if (
                icingaNotifObj.notificationState.lower() == "ok"
                and icingaNotifObj.notificationStateBefore.lower() not in states
            ):
                logging.debug("States does not match, skipping current run")
                continue

            # filter notifications for type & user
            if (
                icingaNotifObj.notificationType.lower() in states
                or icingaNotifObj.notificationState.lower() in states
            ):
                notificationsList.append(icingaNotifObj)
            else:
                logging.debug("States not found in user, skipping current run")
                continue

        # Parse notifications and send them
        # If there are some, parse them and send.
        if len(notificationsList) != 0:
            notificationOutput = parsing.parseNotifications(notificationsList, nType)

            # Type resolution
            if nType == "sms":
                message = "\n".join(notificationOutput)
                ret += sending.sendSMS(smsModem, message, icingaUsers[user.lower()])
            if nType == "email":
                ret += sending.sendMail(smtpServerHost, notificationOutput, icingaUsers[user.lower()])
            if nType == "call":
                (r, lc) = sending.sendCall(
                    lastCall, icingaUsers[user.lower()], callModemObj
                )
                ret += r
                lastCall = lc

    return (ret, lastCall)
