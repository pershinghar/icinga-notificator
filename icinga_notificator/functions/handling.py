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
    slackObj,
    icingaWebUrl,
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
                logging.info(
                    "Cannot handle notifications, something is wrong for this user.."
                )
        except KeyError:
            logging.info("Cannot handle notifications, something is wrong for this user..")
        finally:
            return (1, lastCall)

    options = icingaUsers[user.lower()]["vars"]["notification_options"]

    # Init some things
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

            logging.debug("Notification:")
            logging.debug("\t type: %s", icingaNotifObj.notificationType.lower())
            logging.debug("\t state: %s", icingaNotifObj.notificationState.lower())
            logging.debug(
                "\t stateBefore: %s", icingaNotifObj.notificationStateBefore.lower()
            )
            logging.debug("\t %s : %s", nType, states)

            # filter notifications for type & user
            # if type is problem and state match, append
            if (
                icingaNotifObj.notificationType.lower() == "problem"
                and icingaNotifObj.notificationState.lower() in states
            ):
                notificationsList.append(icingaNotifObj)

            # if type is recovery, and previous state is in states, append
            elif (
                icingaNotifObj.notificationType.lower() == "recovery"
                and icingaNotifObj.notificationStateBefore.lower() in states
                and icingaNotifObj.notificationState.lower() in states
            ):
                notificationsList.append(icingaNotifObj)

            # if type is something else, and matches, append
            elif icingaNotifObj.notificationType.lower() in states:
                notificationsList.append(icingaNotifObj)

            else:
                logging.debug("States not found in user, skipping current run")
                continue

        # Parse notifications and send them
        # If there are some, parse them and send.
        if len(notificationsList) != 0:
            notificationOutput = parsing.parseNotifications(
                notificationsList, nType, icingaWebUrl
            )

            # Type resolution
            if nType == "sms":
                message = "\n".join(notificationOutput)
                ret += sending.sendSMS(smsModem, message, icingaUsers[user.lower()])
            if nType == "email":
                ret += sending.sendMail(
                    smtpServerHost, notificationOutput, icingaUsers[user.lower()]
                )
            if nType == "slack":
                ret += sending.sendSlackMessage(
                    slackObj, notificationOutput, icingaUsers[user.lower()]
                )
            if nType == "call":
                (r, lc) = sending.sendCall(
                    lastCall, icingaUsers[user.lower()], callModemObj
                )
                ret += r
                lastCall = lc

    return (ret, lastCall)
