from icinga_notificator.functions import handling
import test_objects
import pytest
import mock


def test_handleNotifications_BadArgs1():
    # args: NoneType(bad)
    assert handling.handleNotifications(None, None, None, None, None, dict(), None, None, None) == (
        1,
        dict(),
    )


# first two are worth some edits... future
def test_handleNotifications_BadArgs2_mail():
    # args: try some wrong data types
    # prepare test data
    lst = {"pershing": test_objects.icingaUserGen(1).generateOne()}
    for e in ["sms", "call"]:
        lst["pershing"]["vars"]["notification_options"].pop(e)

    assert (
        handling.handleNotifications(
            test_objects.icingaNotifGen().getObj("list"),
            lst,
            "pershing",
            {"bad": "modemdict"},
            "mailserver.something",
            ["this should be dict"],
            ["this should be dict"],
            ["this should be dict"],
            None
        )
        != 0
    )


def test_handleNotifications_BadArgs2_sms():
    # args: try some wrong data types
    # prepare test data
    lst = {"pershing": test_objects.icingaUserGen(1).generateOne()}
    for e in ["email", "call"]:
        lst["pershing"]["vars"]["notification_options"].pop(e)

    assert (
        handling.handleNotifications(
            test_objects.icingaNotifGen().getObj("list"),
            lst,
            "pershing",
            {"bad": "modemdict"},
            "mailserver.something",
            ["this should be dict"],
            ["this should be dict"],
            ["this should be dict"],
            None
        )
        != 0
    )


def test_handleNotifications_BadArgs2_call():
    # args: try some wrong data types
    # prepare test data
    lst = {"pershing": test_objects.icingaUserGen(1).generateOne()}
    for e in ["email", "sms"]:
        lst["pershing"]["vars"]["notification_options"].pop(e)

    assert (
        handling.handleNotifications(
            test_objects.icingaNotifGen().getObj("list"),
            lst,
            "pershing",
            {"bad": "modemdict"},
            "mailserver.something",
            ["this should be dict"],
            ["this should be dict"],
            ["this should be dict"],
            None
        )[0]
        == 1
    )


def test_handleNotifications_BadArgs3():
    u = test_objects.icingaUserGen(10, False).generateOne()
    u["vars"]["notification_options"] = dict()
    uo = {"testuser": u}
    us = "TestUser"
    l = test_objects.icingaNotifGen().getObj("list")

    (r, lc) = handling.handleNotifications(l, uo, us, None, None, None, None, None, None)
    assert r == -1
    assert lc == None


def test_handleNotifications_BadArgs4():
    u = test_objects.icingaUserGen(10, False).generateOne()
    u["vars"].pop("notification_options")
    uo = {"testuser": u}
    us = "TestUser"
    l = test_objects.icingaNotifGen().getObj("list")

    (r, lc) = handling.handleNotifications(l, uo, us, None, None, None, None, None, None)
    assert r == 1
    assert lc == None


@mock.patch("icinga_notificator.functions.sending.sendSMS")
@mock.patch("icinga_notificator.functions.sending.sendMail")
@mock.patch("icinga_notificator.functions.sending.sendCall")
@mock.patch("icinga_notificator.functions.sending.sendSlackMessage")
@mock.patch("icinga_notificator.functions.parsing.parseNotifications")
def test_handleNotifications_BadArgs5(
    mock_parseNotifications, mock_sendSlackMessage, mock_sendCall, mock_sendMail, mock_sendSMS
):
    u = test_objects.icingaUserGen(10, False).generateOne()
    u["vars"]["notification_options"] = {"sms": ["ok"], "email": ["ok"], "call": ["ok"]}
    uo = {"testuser": u}
    us = "TestUser"
    l = test_objects.icingaNotifGen().getObj("list")

    mock_parseNotifications.return_value = "Testing_output"
    mock_sendSMS.return_value = 1
    mock_sendCall.return_value = (1, dict())
    mock_sendMail.return_value = 1
    mock_sendSlackMessage.return_value = 1

    (r, lc) = handling.handleNotifications(l, uo, us, None, None, None, None, None, None)
    assert r >= 1
    assert lc == dict()


@mock.patch("icinga_notificator.functions.sending.sendSMS")
@mock.patch("icinga_notificator.functions.sending.sendMail")
@mock.patch("icinga_notificator.functions.sending.sendCall")
@mock.patch("icinga_notificator.functions.sending.sendSlackMessage")
@mock.patch("icinga_notificator.functions.parsing.parseNotifications")
def test_handleNotifications_OKArgs1(
    mock_parseNotifications, mock_sendSlackMessage, mock_sendCall, mock_sendMail, mock_sendSMS
):

    # try some correct things
    l = test_objects.icingaNotifGen().getObj("list")
    u = test_objects.icingaUserGen(10, False).generateOne()
    uo = {"testuser": u}
    us = "TestUser"

    mock_parseNotifications.return_value = "Testing_output"
    mock_sendSMS.return_value = 1
    mock_sendCall.return_value = (1, dict())
    mock_sendMail.return_value = 1
    mock_sendSlackMessage.return_value = 1

    (r, lc) = handling.handleNotifications(l, uo, us, None, None, None, None, None, None)
    assert r >= 2
    assert lc == dict()

    mock_parseNotifications.assert_called()
    mock_sendSMS.assert_called()
    mock_sendCall.assert_called()
    mock_sendMail.assert_called()
