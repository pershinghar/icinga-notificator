import pytest
import mock
from icinga_notificator.utils import slackLib
from collections import OrderedDict


def test_sendSlackMessage_BadArgs1():
    with pytest.raises(Exception) as e_info:
        assert slackLib.sendSlackMessage(None, None, None)


@mock.patch("urllib.request")
@mock.patch("json.loads")
def test_sendSlackMessage_OKArgs1(mock_json, mock_urllib):
    token = "123"
    username = "jozo"
    text = "anonieanoanie"

    mock_urllib.return_value = "{XX}"
    mock_json.return_value = {"ok": True, "members": [{"name": "jozo", "id": "123"}]}
    assert slackLib.sendSlackMessage(token, username, text) == 0
