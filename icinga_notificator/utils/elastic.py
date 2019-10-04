#!/usr/bin/env/python3
#
# ES Related Functions
#
import logging

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
        logging.exception("Problem with time values - check date/time/code !")
        return 1

    q = query.replace("%%GTE%%", str(timeGreaterThan)).replace("%%LTE%%", str(actTime))

    try:
        ret = esInstance.search(index=index, body=q)
    except:
        logging.exception("Error processing ES query")
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
        logging.exception("Problem with time values - check date/time/code !")
        return 1

    # Insert correct times into query
    q = query.replace("%%GTE%%", str(timeGreaterThan)).replace("%%LTE%%", str(actTime))

    try:
        esInstance.update_by_query(index=index, body=q)

    except Exception as e:
        logging.exception("Problem updating ES - try again later")
        return 2
    else:
        return 0
