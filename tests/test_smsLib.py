import pytest
import mock
from icinga_notificator.utils import smsLib
from collections import OrderedDict


def test_sendSmsEagle_BadArgs1():
    assert smsLib.sendSmsEagle(None, None, None) == 1


@mock.patch("urllib.request")
def test_sendSmsEagle_OKArgs1(mock_urllib):
    smsEagle = {"address": "1.2.3.4", "username": "jozef", "password": "okno"}
    number = "123456"
    text = "anonieanoanie"

    mock_urllib.return_value = "XX"
    assert smsLib.sendSmsEagle(smsEagle, text, number) == 2


@mock.patch("urllib.request")
def test_sendSmsEagle_OKArgs2(mock_urllib):
    smsEagle = {"address": "1.2.3.4", "username": "jozef", "password": "okno"}
    number = "123456"
    text = "anonieanoanie"

    mock_urllib.return_value = "OK;OK"
    assert smsLib.sendSmsEagle(smsEagle, text, number) == 2
