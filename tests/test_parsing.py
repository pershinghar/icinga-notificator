from icinga_notificator.functions import parsing
import test_objects
import pytest
import mock
import logging


def test_parseNotifications_BadArgs1():
    assert parsing.parseNotifications(None, None) == 1


def test_parseNotifications_BadArgs2():
    assert parsing.parseNotifications(123, 456) == 1


def test_parseNotifications_BadArgs3():
    assert parsing.parseNotifications(None, "call") == 1


def test_parseNotifications_BadArgs4():
    assert parsing.parseNotifications(None, "sms") == 1


def test_parseNotifications_BadArgs5():
    assert parsing.parseNotifications([1, 2, 3, 4, 5], "sms") == 1


def test_parseNotifications_OKArgs1(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen().getObj("class")
    o = ["Host(UP): 2000x HOST"]
    assert parsing.parseNotifications(nl, "sms") == o


def test_parseNotifications_OKArgs2(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(count=3).getObj("class")
    tmp = map(lambda x: x.getNormalOutput(), nl)
    o = list(tmp)
    print(o)
    assert parsing.parseNotifications(nl, "sms") == o


def test_parseNotifications_OKArgs3(caplog):
    c = 3
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(count=c).getObj("class")
    out = parsing.parseNotifications(nl, "email").get_payload()[0].get_payload()
    assert len(out.split("\n")) == 8 and out.split("\n")[0:3] == ["OK: 1x", "WARNING: 1x", "CRITICAL: 1x"]


def test_parseNotifications_OKArgs4(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(serviceCount=3).getObj("class")
    o = ["test.ls.intra: 2000x SERVICE"]
    assert parsing.parseNotifications(nl, "sms") == o

def test_parseNotifications_OKArgs5(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(count=5, serviceCount=5).getObj("class")
    o = ["test.ls.intra: test.ls.intra0!service test.ls.intra1!service test.ls.intra2!service test.ls.intra3!service "
         "test.ls.intra4!service "]
    assert parsing.parseNotifications(nl, "sms") == o


def test_parseNotifications_OKArgs6(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(count=5, hostCount=3, serviceCount=2).getObj("class")
    o = ['test.ls.intra0: 2', 'test.ls.intra1: 2', 'test.ls.intra2: 1']
    assert parsing.parseNotifications(nl, "sms") == o


def test_parseNotifications_OKArgs7(caplog):
    caplog.set_level(logging.DEBUG)
    nl = test_objects.icingaNotifGen(count=5, hostCount=1, serviceCount=1).getObj("class")
    o = ['test.ls.intra0!service: test.ls.intra0 test.ls.intra0 test.ls.intra0 test.ls.intra0 test.ls.intra0 ']
    assert parsing.parseNotifications(nl, "sms") == o


# def test_parseNotifications_OKArgs3(caplog):
#    caplog.set_level(logging.DEBUG)
#    nl = test_objects.icingaNotifGen(count=10).getObj("class")
#    tmp = map(lambda x: x.getNormalOutput(), nl)
#    o = list(tmp)
#    print(o)
#    assert parsing.parseNotifications(nl, "sms") == o
