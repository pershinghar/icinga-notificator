#!/usr/bin/env/python3
#
# Definitions of notification handlers
#
# various methods
#

import logging
import smtplib
import socket

import paramiko
from collections import OrderedDict
import subprocess
import time
from icinga_notificator.utils import smsLib
from icinga_notificator.utils import slackLib

#
# MAIL
#


def sendMail(smtpServerHost, message, icingaUser):
    """ Function which process email sending """

    # Define default subject - can be changed later
    if icingaUser is None or type(icingaUser) is not dict:
        raise Exception("Bad icingaUser format, should be dict")

    if "email" not in icingaUser:
        logging.error("Cannot send email to user %s", icingaUser)
        return 1
    receiver_email = icingaUser["email"]
    sender_email = socket.gethostname() + "@" + socket.getfqdn().split(".", 1)[-1]
    subject = "Icinga Notifications from " + socket.gethostname()
    logging.info("Sending EMAIL to %s", receiver_email)
    logging.debug("Content: %s", message.as_string())

    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    r = 1

    try:
        # Send messages
        mailServer = smtplib.SMTP(smtpServerHost, 25, timeout=10)
        mailServer.sendmail(sender_email, receiver_email, message.as_string())
        r = 0
    except Exception:
        logging.exception("Error sending mail!")
        r = 1
    return r


#
# SMS
#


def sendSMS(smsModem, message, icingaUser):
    """ Function which process sms sending """

    pager = icingaUser["pager"]
    logging.info("Sending MESSAGE to - tel %s", pager)
    logging.debug("Content: %s", message)

    # default return goes to error
    r = 2

    try:
        # Send SMS via SMS eagle API
        r = smsLib.sendSmsEagle(smsModem, message, pager)
    except Exception:
        logging.exception("Error sending SMS!")

    return r


#
# Slack personal
#
def sendSlackMessage(slackObj, message, icingaUser):
    """ Function which uses slack to send message to user """

    logging.info("Sending SLACK MESSAGE to - user %s", icingaUser["name"])
    logging.debug("Content: %s", message)

    # let's only call external function..
    username = icingaUser["name"]
    token = slackObj["bottoken"]
    # default return value
    r = 2

    try:
        r = slackLib.sendSlackMessage(token, username, message)
    except Exception:
        logging.exception("Error sending slack message!")

    return r


#
# CALL
#


def sendCall(lastCall, icingaUser, callModemObj):
    """ Function which process calling to users (pager notifications)"""

    if icingaUser is not None and "pager" in icingaUser:
        pager = icingaUser["pager"]
    else:
        logging.error("User does not have number, cannot call")
        return (1, lastCall)

    # some checks for corect data types
    if callModemObj is None or type(callModemObj) is not OrderedDict:
        logging.error("Wrong settings of call modem - check config/code -")
        return (1, lastCall)

    # Create command for calling (add number)
    cmd = callModemObj["cmd"].replace("##PAGER##", str(pager))
    # Count if call for user was not done vars_before
    nowTime = int(round(time.time() * 1000))
    try:
        if pager in lastCall.keys():
            diff = nowTime - lastCall[pager]
            # Dont call if time between calls is lower than 30min !
            if diff < 1800000:
                logging.info("Skipping call to %s - due to timer", pager)
                return (0, lastCall)

    except (KeyError, AttributeError):
        logging.error("Wrong type of lastcall, should be dict", exc_info=True)
        return (1, lastCall)

    # Update lastCall time
    logging.info("Run: Send CALL to %s", pager)
    lastCall[pager] = nowTime

    # Process CALL
    # If there is LOCAL setting
    if callModemObj["host"] == "LOCAL":
        # Run script locally
        try:
            scriptCall = subprocess.run([cmd], shell=True)
            if scriptCall.returncode != 0:
                logging.error(
                    "Error calling [LOCAL-script returned " + scriptCall.returncode + "]"
                )
                return (1, lastCall)
        except:
            logging.exception("Error when trying to run callScript locally")
            return (1, lastCall)

    # If there is NONE, we skip calling (We don't have modem)
    elif callModemObj["host"] == "NONE":
        logging.debug("Calling isn't supported on this instance(checkconf)")
        return (0, lastCall)

    # If there is modem specified
    else:
        try:
            ssh = paramiko.SSHClient()
            k = paramiko.RSAKey.from_private_key_file(callModemObj["sshkey"])
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(callModemObj["host"], username=callModemObj["user"])
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
            logging.debug(ssh_stdout.read())
            logging.debug(ssh_stderr.read())

        except paramiko.SSHException:
            logging.exception("Error while trying to connect to callModemHost-ssh,")
            return (1, lastCall)

        except OSError:
            logging.exception("SSH Private key not fount, error calling")
            return (1, lastCall)
        else:
            ssh.close()

    return (0, lastCall)
