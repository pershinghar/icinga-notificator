#!/usr/bin/env/python3
#
# Notification parsing (manipulating)
#
import json
import logging
import configparser
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from string import Template

from icinga_notificator.functions import aggregation


def parseNotifications(notificationsToParse, form, icingaWebUrl=None):
    """ Function which parses notifications by type of sending channel - sms/email/etc """
    notificationOutput = list()

    if notificationsToParse is None or type(notificationsToParse) is not list:
        return 1

    if form == "call":
        # We call, so we only ensure something is returned
        notificationOutput.append("dummy")

    if form in ["sms", "email", "slack"]:
        # If less than 4, send separately with description
        if len(notificationsToParse) < 4 or form == "email" or form == "slack":
            for notif in notificationsToParse:
                output = (
                    notif.getNormalOutput()
                    if form == "sms"
                    else notif.getNormalOutput(verbose=True)
                )
                notificationOutput.append(output)
                logging.debug("[parsing1]: %s", output)

        # If more than 4, do some research and group it by host / service
        elif len(notificationsToParse) >= 4:
            # Create aggregated dictionaries - aggregation by host or service
            perHost = aggregation.aggregateBy(notificationsToParse, "host")
            perService = aggregation.aggregateBy(notificationsToParse, "service")

            # error situations
            if perHost == 1 or perService == 1:
                return 1

            output = ""
            if len(perService) == 1:
                for service, notif in perService.items():
                    if len(perService[service]) <= 5:
                        output = service + ": "
                        for nc in notif:
                            output += nc.host + " "
                    else:
                        output = service + ": " + str(len(perService[service])) + "x HOST"

                    notificationOutput.append(output)
                    logging.debug("[parsing2]: %s", output)

            elif len(perHost) <= 2:
                for host, notif in perHost.items():
                    if len(notif) <= 5:
                        output = host + ": "
                        for nc in notif:
                            output += nc.service + " "
                    else:
                        output = host + ": " + str(len(perHost[host])) + "x SERVICE"

                    notificationOutput.append(output)
                    logging.debug("[parsing3]: %s", output)

            elif len(perHost) > 2:
                for host, notif in perHost.items():
                    output = host + ": " + str(len(perHost[host]))

                    notificationOutput.append(output)
                    logging.debug("[parsing4]: %s", output)

    if form == "slack":
        hostUrlTemp = Template(icingaWebUrl + '/dashboard#!/monitoring/host/show?host=$host')
        serviceUrlTemp = Template(icingaWebUrl + '/dashboard#!/monitoring/service/show?host=$host&service=$service')

        summary = dict()

        # Fill summary with key=state, value=markdown link to Icinga
        for item in notificationsToParse:
            tmp = item.getNormalOutput().split(": ")[1].split(" ")[0]
            host = item.getNormalOutput().split(" - ")[0]
            link = "<" + hostUrlTemp.substitute(host=host) + "|" + host \
                if "!" not in tmp \
                else tmp.split("!")[0] + " - <" + \
                     serviceUrlTemp.substitute(host=tmp.split("!")[0], service=tmp.split("!")[-1]) + "|" + \
                     tmp.split("!")[-1]
            link += ">: " + item.strippedMessage + ". " + item.optionalMessage
            try:
                summary[item.getNormalOutput().split(" - ")[1].split(":")[0]].append(link)
            except KeyError:
                summary[item.getNormalOutput().split(" - ")[1].split(":")[0]] = [link]

        body = "*Icinga alert:*\n"
        logging.info(summary)
        for k in summary.keys():
            if k == "CRITICAL":
                body += ":red_circle:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
            elif k == "UNKNOWN":
                body += ":large_blue_circle:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
            elif k == "WARNING":
                body += ":warning:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
            elif k == "ACKNOWLEDGEMENT":
                body += ":white_check_mark:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
            elif k == "CUSTOM":
                body += ":arrow_right:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
            elif k == "OK":
                body += ":green_heart:" + " *" + k + ":*\n\t" + "\n\t".join(summary[k]) + "\n"
        return body

    if form == "email":
        # Create e-mail object
        summary = dict()
        for item in notificationOutput:
            try:
                summary[item.split(" - ")[1].split(":")[0]].append(item.split(" - ")[0])
            except KeyError:
                summary[item.split(" - ")[1].split(":")[0]] = [item.split(" - ")[0]]
        body = ""
        for k, v in summary.items():
            body += k + ": " + str(len(v)) + "x\n"
        body += "\n".join(notificationOutput)

        body += "\n" + "=" * 10 + "\n"

        message = MIMEMultipart()
        message.attach(MIMEText(body, "plain"))

        filename = "/tmp/report.json"

        output_json = dict()
        output_json["root"] = list()

        for n in notificationsToParse:
            output_json["root"].append(n.objIcinga)

        with open(filename, "w") as file:
            json.dump(output_json, file)

        # Attach json to e-mail
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        encoders.encode_base64(part)

        part.add_header("Content-Disposition", "attachment; filename= " + filename)

        message.attach(part)
        return message

    return notificationOutput
