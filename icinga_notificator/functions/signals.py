#!/usr/bin/env/python3
#
#   Signal functions used to control script
#

import logging


def signalHandler(sig, frame):
    """ Simple function to handle singnals """
    # can be improved
    logging.debug("%s detected", sig)
    logging.info("icinga-notificator exited (%s)", sig)
    exit(0)
