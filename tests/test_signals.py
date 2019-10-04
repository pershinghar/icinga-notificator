from icinga_notificator.functions import signals
import pytest


def test_signalHandler_BadArgs1():
    with pytest.raises(SystemExit):
        signals.signalHandler("SIG", "yes")
