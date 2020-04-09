#!/usr/bin/env/python3
#
# SMS sending LIB
#

# compatibility removed (py2)

import logging
import urllib

# Sending function - using SMS Eagle API
# sendSmsEagle(dict, str, str)
# smsEagle object needs to have - address, user, pass keys.


def sendSmsEagle(smsEagle, text, number):
    """ Function to send sms via smseagle modem and its API """
    try:
        baseUrl = "http://" + smsEagle["address"] + "/index.php/http_api/send_sms"
        args = {
            "login": smsEagle["username"],
            "pass": smsEagle["password"],
            "to": number,
            "message": text,
        }
    except KeyError:
        logging.error("[smsLib.py] Error parsing args for smsEagle modem, cannot send sms")
        logging.debug("Debug info:", exc_info=True)
        return 1
    except TypeError:
        logging.error("[smsLib.py] Error in function args, cannot send sms")
        logging.debug("Debug info:", exc_info=True)
        return 1

    encodedArgs = urllib.parse.urlencode(args)
    url = baseUrl + "?" + encodedArgs
    with urllib.request.urlopen(url) as response:
        result = response.read().decode("utf-8")

    logging.debug("sms url: %s", url)
    logging.debug("result: %s", result)

    if result.split(";")[0].strip() == "OK":
        r = 0
    else:
        r = 2
    return r
