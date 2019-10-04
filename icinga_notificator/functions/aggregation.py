#!/usr/bin/env/python3
#
# Aggregation es result by host/services/etc
#
import logging
from icinga_notificator.classes import icingaNotification


def aggregateBy(notificationsToAgg, by):
    """
    Aggregate notifications by some parameter (host, service)
    """
    aggregated = dict()

    if type(notificationsToAgg) is not list or len(notificationsToAgg) == 0:
        logging.error("Aggregate error, not continuing (notifies); %s", notificationsToAgg)
        return 1
    if type(by) is not str or len(by) == 0:
        logging.error("Aggregate error, not continuing (by); %s", by)
        return 1

    for notification in notificationsToAgg:

        if type(notification) is dict:
            # IF we use RAW data -
            # from elastic -
            # this shit should be replaced with something more nice

            # Just to make things more simple
            nData = notification["_source"]["icinga"]

            # If service is not defined - we create some dummy called host
            if by not in nData:
                nData[by] = "Host(UP)"

            if type(nData[by]) is list:
                for key in nData[by]:
                    if key not in aggregated:
                        aggregated[key] = list()
                        aggregated[key].append(notification)
                    else:
                        aggregated[key].append(notification)

            else:
                key = nData[by]
                if key not in aggregated:
                    aggregated[key] = list()
                    aggregated[key].append(notification)
                else:
                    aggregated[key].append(notification)
        elif isinstance(notification, icingaNotification.icingaNotification):
            # Or WE use object
            # Just to make things more simple
            nData = notification.obj["_source"]["icinga"]

            if by not in nData:
                nData[by] = "Host(UP)"

            if type(nData[by]) is list:
                for key in nData[by]:
                    if key not in aggregated:
                        aggregated[key] = list()
                        aggregated[key].append(notification)
                    else:
                        aggregated[key].append(notification)

            else:
                key = nData[by]
                if key not in aggregated:
                    aggregated[key] = list()
                    aggregated[key].append(notification)
                else:
                    aggregated[key].append(notification)
        else:
            logging.error("Not aggregating, types not matched !")
            return 1

    return aggregated
