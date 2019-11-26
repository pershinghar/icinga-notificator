#!/usr/bin/env/python3
#
# icinga notification class definition
#

import logging
from icinga_notificator.base import consts


class icingaNotification:
    """
    Class object for handling notifications.
    On init
    - you load ES notification object (Returned from ES query)
    - it gets parsed, then you can do some operations with it.
    """

    def __init__(self, notificationObject, user):
        """Parse es query, assign object, host and other vars"""
        try:
            self.obj = notificationObject
            self.objIcinga = notificationObject["_source"]["icinga"]
            self.host = str(notificationObject["_source"]["icinga"]["host"])
        except (TypeError, KeyError, AttributeError) as e:
            logging.error("Error initializing notificationObject")
            raise e

        # Detect If we are dealing with host or service
        if "service" in self.objIcinga:
            self.service = str(self.objIcinga["service"])
        else:
            self.service = "HOST"

        self.rawMessage = str(self.objIcinga["check_result"]["output"])

        # Remove unnecessary strings from output
        self.message = str(
            self.objIcinga["check_result"]["output"]
                .replace("\n", " ")
                .replace("CRITICAL - ", "")
                .replace("WARNING - ", "")
        )

        # create shortened message
        self.strippedMessage = str(self.message[:100] + (self.message[100:] and ".."))

        # If some optional text provided, include it.
        self.optionalMessage = str(" " + self.objIcinga["text"])

        # Fill check result info (also before)
        self.checkResult = self.objIcinga["check_result"]["state"]

        self.checkResultBefore = self.objIcinga["check_result"]["vars_before"]["state"]

        self.checkResultBeforeType = self.objIcinga["check_result"]["vars_before"][
            "state_type"
        ]

        try:
            self.notificationState = consts.EXITCODES[self.checkResult]
        except KeyError:
            self.notificationState = "CRITICAL"

        try:
            self.notificationStateBefore = consts.EXITCODES[self.checkResultBefore]
        except KeyError:
            self.notificationStateBefore = "CRITICAL"

        self.notificationType = str(self.objIcinga["notification_type"])
        self.user = str(user)

    def getNormalOutput(self, verbose=False):
        """ Parse string output from notification object - human readable"""
        if self.notificationType == "PROBLEM":
            output = (
                    self.host
                    + " - "
                    + self.notificationState
                    + ": "
                    + self.service
                    + " "
                    + (self.strippedMessage if not verbose else self.message).rstrip()
                    + "."
                    + self.optionalMessage
            )

        elif self.notificationType == "RECOVERY":
            output = (
                    self.host
                    + " - "
                    + self.notificationState
                    + ": "
                    + self.service
                    + self.optionalMessage
            )


        elif self.notificationType in ["ACKNOWLEDGEMENT", "CUSTOM", "DOWNTIMESTART", "DOWNTIMEEND", "DOWNTIMEREMOVED",
                                       "FLAPPINGSTART", "FLAPPINGEND"]:
            output = (
                    self.host
                    + " - "
                    + self.notificationType
                    + ": "
                    + self.service
                    + " - "
                    + self.optionalMessage
            )

        else:
            output = (
                    self.host
                    + " - PROBLEM: "
                    + self.service
                    + " "
                    + (self.strippedMessage if not verbose else self.message)
                    + "."
                    + self.optionalMessage
            )

        return output.strip()
