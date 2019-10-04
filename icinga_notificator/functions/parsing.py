#!/usr/bin/env/python3
#
# Notification parsing (manipulating)
#
import logging, email, smtplib, ssl, json
import string
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from icinga_notificator.functions import aggregation


def parseNotifications(notificationsToParse, form):
    """ Function which parses notifications by type of sending channel - sms/email/etc """
    notificationOutput = list()

    if notificationsToParse is None or type(notificationsToParse) is not list:
        return 1

    if form == "call":
        # We call, so we only ensure something is returned
        notificationOutput.append("dummy")

    if form == "sms" or form == "email":
        # If less than 4, send separatelly with description
        if len(notificationsToParse) < 4 or form == "email":
            for notif in notificationsToParse:
                output = notif.getNormalOutput() if form == "sms" else notif.getNormalOutput(verbose=True)
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

        body += "\n" + "="*10 + "\n"

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

        part.add_header(
            "Content-Disposition",
            "attachment; filename= " + filename,
        )

        message.attach(part)
        return message

    return notificationOutput

