from icinga_notificator.classes import icingaNotification
import test_objects
import pytest


def test_icingaNotification_BadArgs1():
    with pytest.raises(TypeError):
        assert icingaNotification.icingaNotification(None, None)


def test_icingaNotification_BadArgs2():
    o = test_objects.icingaNotifGen().getObj("list")
    with pytest.raises(TypeError):
        assert icingaNotification.icingaNotification(o, None)


def test_icingaNotification_BadArgs3():
    o = test_objects.icingaNotifGen().getObj("list")[0]["_source"]["icinga"].pop("host")
    with pytest.raises(TypeError):
        assert icingaNotification.icingaNotification(o, "user")


def test_icingaNotification_getNormalOutput_BadArgs1():
    o = (
        test_objects.icingaNotifGen()
        .getObj("list")[0]["_source"]["icinga"]
        .pop("check_result")
    )
    with pytest.raises(KeyError):
        assert icingaNotification.icingaNotification(o, None).getNormalOutput()


def test_icingaNotification_BasicInit1():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    assert icingaNotification.icingaNotification(o, "user")


def test_icingaNotification_BasicInit2():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    o["_source"]["icinga"]["service"] = "Dummy"

    assert icingaNotification.icingaNotification(o, "user")


def test_icingaNotification_getOutput1():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    o["_source"]["icinga"]["check_result"]["state"] = "44"
    o["_source"]["icinga"]["check_result"]["vars_before"]["state"] = "55"
    o["_source"]["icinga"]["notification_type"] = "PROBLEM"
    assert (
        icingaNotification.icingaNotification(o, "user").getNormalOutput()
        == "test.ls.intra - CRITICAL: HOST dummy output. test text"
    )


def test_icingaNotification_getOutput2():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    o["_source"]["icinga"]["notification_type"] = "RECOVERY"
    o["_source"]["icinga"]["check_result"]["state"] = 0
    assert (
        icingaNotification.icingaNotification(o, "user").getNormalOutput()
        == "test.ls.intra - OK: HOST test text"
    )


def test_icingaNotification_getOutput3():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    o["_source"]["icinga"]["notification_type"] = "CUSTOM"

    assert (
        icingaNotification.icingaNotification(o, "user").getNormalOutput()
        == "test.ls.intra - CUSTOM: HOST - test text"
    )


def test_icingaNotification_getOutput4():
    o = test_objects.icingaNotifGen(1).getObj("list")[0]
    o["_source"]["icinga"]["notification_type"] = "IMPOSSIBLE"

    assert (
        icingaNotification.icingaNotification(o, "user").getNormalOutput()
        == "test.ls.intra - PROBLEM: HOST dummy output. test text"
    )
