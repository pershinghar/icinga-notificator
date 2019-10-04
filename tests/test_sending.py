from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from icinga_notificator.functions import sending
import test_objects
import pytest
import mock
import socket
import time
from collections import OrderedDict
from paramiko import SSHException

# need to define test for every type

# TODO: Change e-mail sending tests
def test_sendMail_BadArgs1():
    with pytest.raises(Exception):
        assert sending.sendMail(None, None, None)


def test_sendMail_BadArgs2():
    testList = test_objects.icingaUserGen(200, True, True, 120).generateList()
    for i in testList:
        assert sending.sendMail(213, MIMEMultipart(), i) == 1


def test_sendMail_BadArgs3():
    assert (
        sending.sendMail(
            {"a": "b"}, MIMEMultipart(), test_objects.icingaUserGen(1, False).generateOne()
        )
        == 1
    )


@mock.patch("smtplib.SMTP")
def test_sendMail_process1(mock_SMTP):
    mock_SMTP.return_value = 0
    assert (
        sending.sendMail(
            {"a": "b"}, MIMEMultipart(), test_objects.icingaUserGen(1, False).generateOne()
        )
        == 1
    )


@mock.patch("smtplib.SMTP")
def test_sendMail_process2(mock_SMTP):

    # Build args we expect
    sender = socket.gethostname() + "@" + socket.getfqdn().split(".", 1)[-1]
    u = test_objects.icingaUserGen(1, False).generateOne()

    message = MIMEMultipart()
    umail = u["email"]

    message["From"] = sender
    message["To"] = umail
    message["Subject"] = "Icinga Notifications from " + socket.gethostname()
    message.attach(MIMEText("test", "plain"))

    sending.sendMail({"a": "b"}, message, u)
    mock_SMTP.return_value.sendmail.assert_called_once_with(sender, umail, message.as_string())


def test_sendCall_BadArgs1():
    assert sending.sendCall(None, None, None) == (1, None)


def test_sendCall_BadArgs2():
    assert sending.sendCall(None, None, OrderedDict()) == (1, None)


def test_sendCall_BadArgs3():
    callModemObj = OrderedDict(
        [("host", "undefined"), ("sshkey", "/usr/ltts"), ("cmd", "/bin/false")]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    assert sending.sendCall(None, u, callModemObj) == (1, None)


def test_sendCall_BadArgs4():
    callModemObj = OrderedDict(
        [("host", "undefined"), ("sshkey", "/usr/ltts"), ("cmd", "/bin/false")]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000))

    assert sending.sendCall({p: t}, u, callModemObj)[0] == 0


def test_sendCall_BadArgs5():
    callModemObj = OrderedDict(
        [("host", "undefined"), ("sshkey", "/usr/ltts"), ("cmd", "/bin/false")]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    assert sending.sendCall({p: t}, u, callModemObj)[0] == 1


class readDummy:
    def __init__(self):
        init = 1

    def read(self):
        return 0


# so complicated test for me.e..
@mock.patch("paramiko.SSHClient")
@mock.patch("paramiko.RSAKey")
@mock.patch("paramiko.SSHClient.exec_command")
def test_sendCall_BadArgs6(mock_SSHClient, mock_RSAkey, mock_exec_command):
    callModemObj = OrderedDict(
        [
            ("host", "undefined"),
            ("sshkey", "/dev/null"),
            ("cmd", "/bin/false"),
            ("user", "test"),
        ]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    mock_RSAkey.from_private_key_file.return_value = 0
    mock_exec_command.return_value.exec_command.return_value = (
        readDummy(),
        readDummy(),
        readDummy(),
    )

    sending.sendCall({p: t}, u, callModemObj)
    mock_exec_command.assert_called()


@mock.patch("paramiko.SSHClient")
def test_sendCall_BadArgs7(mock_SSHClient):
    callModemObj = OrderedDict(
        [
            ("host", "undefined"),
            ("sshkey", "/dev/null"),
            ("cmd", "/bin/false"),
            ("user", "test"),
        ]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    mock_SSHClient.return_value.side_effect = Exception(SSHException)
    assert sending.sendCall({p: t}, u, callModemObj)[0] == 1


def test_sendCall_BadArgs8():
    callModemObj = OrderedDict(
        [("host", "NONE"), ("sshkey", "/dev/null"), ("cmd", "/bin/false")]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    assert sending.sendCall({p: t}, u, callModemObj)[0] == 0


@mock.patch("subprocess.run")
def test_sendCall_BadArgs9(mock_run):
    callModemObj = OrderedDict([("host", "LOCAL"), ("sshkey", None), ("cmd", "/bin/false")])
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    mock_run.return_value.run.return_value = 1

    assert sending.sendCall({p: t}, u, callModemObj)[0] == 1


@mock.patch("subprocess.run")
def test_sendCall_OKArgs1(mock_run):
    callModemObj = OrderedDict(
        [("host", "LOCAL"), ("sshkey", "/dev/null"), ("cmd", "/bin/false")]
    )
    u = test_objects.icingaUserGen(1, False).generateOne()
    p = u["pager"]
    t = int(round(time.time() * 1000)) - 1900000

    mock_run.return_value = 0

    assert sending.sendCall({p: t}, u, callModemObj)[0] == 1
