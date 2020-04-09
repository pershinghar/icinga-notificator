#!/usr/bin/env/python3
#
# Get users from icinga API via urllib requests
#
# python2 compatibility removed !


import logging
import urllib.parse
import urllib.request
import urllib.error
import urllib
import ssl
import json
from collections import OrderedDict


def getIcingaUsers(icingaApi):
    """ Function to download users from icinga api """
    # Get user list from API and parse it as DICT for nicknames
    users = dict()

    if type(icingaApi) is not OrderedDict:
        logging.error("[getUsers.py] Wrong type of icingaApi config object, error!")
        raise (TypeError)

    if "cafile" not in icingaApi:
        icingaApi["cafile"] = "/var/lib/icinga2/certs/ca.crt"

    try:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_verify_locations(icingaApi["cafile"])
        httpsHandler = urllib.request.HTTPSHandler(context=context)

        pwMgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
        pwMgr.add_password(
            None, icingaApi["url"], icingaApi["username"], icingaApi["password"]
        )

        authHandler = urllib.request.HTTPBasicAuthHandler(pwMgr)

        opener = urllib.request.build_opener(authHandler, httpsHandler)
        opener.open(icingaApi["url"])
        urllib.request.install_opener(opener)
        with urllib.request.urlopen(icingaApi["url"]) as response:
            tmp = response.read().decode("utf-8")
            data = json.loads(tmp)

    except Exception as e:
        logging.debug("[getUsers.py] Exception when trying to download users from API")
        raise (e)

    try:
        for user in data["results"]:
            username = str(user["attrs"]["__name"]).lower()
            users[username] = user["attrs"]
    except (KeyError, TypeError) as e:
        logging.error(
            "[getUsers.py] Downloaded users are not in form script expects.. cannot parse"
        )
        logging.debug("Debug info:", exc_info=True)
        return 3
    return users
