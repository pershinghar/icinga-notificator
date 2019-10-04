from icinga_notificator.utils import getUsers
import pytest
import mock
import urllib
from collections import OrderedDict


def test_getIcingaUsers_OtherArgTypeHandling():
    # we test only negative answers
    assert getUsers.getIcingaUsers(None) == 1


def test_getIcingaUsers_BadArgs1():
    # Try to pass some bad dict
    icingaApi = {"badKey": "apiUser", "url": "http://somebadthings"}

    assert getUsers.getIcingaUsers(icingaApi) == 1


def test_getIcingaUsers_BadArgs2():
    # Try to pass some bad dict
    icingaApi = OrderedDict()

    assert getUsers.getIcingaUsers(icingaApi) == 2


@mock.patch("urllib.request")
@mock.patch("json.loads")
@mock.patch("ssl.SSLContext.load_verify_locations")
def test_getIcingaUsers_BadArgs3(mock_urlopen, mock_json, mock_sslverify):
    icingaApi = OrderedDict(
        [
            ("cafile", "/etc/passwd"),
            ("username", "Test"),
            ("password", "test"),
            ("url", "https://localhost"),
        ]
    )

    testJson = '{ "test" : "test" }'
    mock_sslverify.retun_value = 0
    mock_urlopen.OpenerDirector.open.return_value = 0
    mock_urlopen.urlopen.return_value = testJson
    mock_json.return_value = dict()

    assert getUsers.getIcingaUsers(icingaApi) == 3
    mock_urlopen.assert_called()


@mock.patch("urllib.request")
@mock.patch("json.loads")
@mock.patch("ssl.SSLContext.load_verify_locations")
def test_getIcingaUsers_BadArgs4(mock_urlopen, mock_json, mock_sslverify):
    icingaApi = OrderedDict(
        [
            ("cafile", "/etc/passwd"),
            ("username", "Test"),
            ("password", "test"),
            ("url", "https://localhost"),
        ]
    )

    testJson = '{ "test" : "test", "results" : "test" }'
    testDict = {"results": {"attrs": "no"}}
    mock_sslverify.retun_value = 0
    mock_urlopen.OpenerDirector.open.return_value = 0
    mock_urlopen.urlopen.return_value = testJson
    mock_json.return_value = testDict

    assert getUsers.getIcingaUsers(icingaApi) == 3
    mock_urlopen.assert_called()


@mock.patch("urllib.request")
@mock.patch("json.loads")
@mock.patch("ssl.SSLContext.load_verify_locations")
def test_getIcingaUsers_OKArgs1(mock_urlopen, mock_json, mock_sslverify):
    icingaApi = OrderedDict(
        [
            ("cafile", "/etc/passwd"),
            ("username", "Test"),
            ("password", "test"),
            ("url", "https://localhost"),
        ]
    )

    testJson = '{ "test" : "test", "results" : "test" }'
    testDict = {"results": [{"attrs": {"__name": "Jozko"}}, {"attrs": {"__name": "Janko"}}]}
    expectDict = {"jozko": {"__name": "Jozko"}, "janko": {"__name": "Janko"}}
    mock_sslverify.retun_value = 0
    mock_urlopen.OpenerDirector.open.return_value = 0
    mock_urlopen.urlopen.return_value = testJson
    mock_json.return_value = testDict

    assert getUsers.getIcingaUsers(icingaApi) == expectDict
