#!/usr/bin/env/python3
#
# ES Related Functions
#
import logging
import urllib

#
# Basic Query function; includes time range counting
#


def queryEs(esInstance, index, query, timePer, actTime):
    """
    Elastic Query function with time parsing, for querying notifications
    """
    try:
        timeGreaterThan = int(actTime) - (1000 * int(timePer))
    except (ValueError, KeyError, AttributeError, TypeError) as e:
        logging.error("[elastic.py] Problem with time values(Query) - check date/time/code")
        logging.debug("Debug info:", exc_info=True)
        return 1

    q = query.replace("%%GTE%%", str(timeGreaterThan)).replace("%%LTE%%", str(actTime))

    try:
        ret = esInstance.search(index=index, body=q)
    except Exception as e:
        logging.error("[elastic.py] Error processing ES query")
        logging.debug("Debug info:", exc_info=True)
        return 2

    return ret


#
# Update Query function - marking notifications as handled
#


def markAsHandled(esInstance, index, query, timePer, actTime):
    """
    Elastic query function (update by query) with time parsing, for updating notifications status
    """
    try:
        # Count GTE value
        timeGreaterThan = int(actTime) - (1000 * int(timePer))
    except (ValueError, KeyError, AttributeError, TypeError) as e:
        logging.error(
            "[elastic.py] Problem with time values(MarkAsHandled) - check date/time/code!"
        )
        logging.debug("Debug info:", exc_info=True)

        return 1

    # Insert correct times into query
    q = query.replace("%%GTE%%", str(timeGreaterThan)).replace("%%LTE%%", str(actTime))

    try:
        esInstance.update_by_query(index=index, body=q)

    except Exception:
        logging.error("[elastic.py] Problem updating ES")
        logging.debug("Debug info:", exc_info=True)
        return 2
    else:
        return 0


def checkMasterStatus(esHost, esPort):
    # run only if you are master ! (got from es status)
    url = "http://" + esHost + ":" + esPort + "/_cat/nodes?h=name,master"
    with urllib.request.urlopen(url) as response:
        res = response.read()
    masterStatus = dict()
    for server in res.decode("utf-8").split("\n"):
        if server == "":
            continue
        masterStatus[server.split()[0]] = server.split()[1]

    return masterStatus
