from icinga_notificator.classes import icingaNotification
import string
import random


# some tools
# EXITCODES = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN"}


def randomString(stringLength=10):
    # Generate a random string of fixed length
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))


# generate some list of notifications(obj from elastic, class)
class icingaNotifGen:
    def __init__(self, count=2000, serviceCount=0, hostCount=0, notificationType="PROBLEM"):
        self.notifyRawList = list()
        self.notifyClassList = list()

        # generate
        for i in range(0, count):
            obj = {
                "_source": {
                    "icinga": {
                        "a": "1",
                        "b": str(random.random()),
                        "d": ["one", "two"],
                        "check_result": {
                            "output": "dummy output",
                            "state": i % 4,
                            "vars_before": {
                                "state": i % 4,
                                "state_type": "dummy state type",
                            },
                        },
                        "text": "test text",
                        "notification_type": notificationType,
                        "users": ["testuser"],
                    }
                }
            }
            if serviceCount > 0:
                obj["_source"]["icinga"]["service"] = "test.ls.intra" + str(i % serviceCount) + "!service"
            obj["_source"]["icinga"]["host"] = "test.ls.intra" + str(i % hostCount) if hostCount > 0 else "test.ls" \
                                                                                                          ".intra"
            c = icingaNotification.icingaNotification(obj, "dummy")
            self.notifyRawList.append(obj)
            self.notifyClassList.append(icingaNotification.icingaNotification(obj, "dummy"))

    def getObj(self, typeOf):
        if typeOf == "list":
            return self.notifyRawList
        if typeOf == "class":
            return self.notifyClassList


# user generation class, sophistically generates data
class icingaUserGen:
    def __init__(self, count, generateIncomplete=False, ok=True, brutal=10):
        self.ok = ok
        self.count = count
        self.generateIncomplete = generateIncomplete
        self.brutal = brutal

    def getTemplate(self):
        if self.ok is True:
            ret = {
                "pager": "12345678",
                "email": randomString(self.brutal),
                "display_name": randomString(self.brutal),
                "vars": {
                    "oncall": "True",
                    "notification_options": {
                        "sms": ["ok", "critical"],
                        "email": ["unknown", "critical"],
                        "call": ["critical"],
                    },
                },
            }
        else:
            ret = {
                "pager": randomString(self.brutal),
                "email": randomString(self.brutal),
                "display_name": randomString(self.brutal),
                "vars": {
                    "oncall": randomString(self.brutal),
                    "notification_options": {
                        "sms": randomString(self.brutal),
                        "email": randomString(self.brutal),
                        "call": randomString(self.brutal),
                    },
                },
            }

        return ret

    def generateList(self):
        ret = list()
        for i in range(0, self.count):
            n = self.getTemplate()
            if self.generateIncomplete is True:
                if i % 3:
                    n.pop("pager")
                if i % 13:
                    n.pop("email")
                if i % 8:
                    n.pop("vars")
            ret.append(n)
        return ret

    def generateOne(self):
        return self.getTemplate()
