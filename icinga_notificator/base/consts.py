#!/usr/bin/env/python3
#
# CONSTs definition
#

""" This dict is for mapping icinga return codes to string value"""
EXITCODES = {0: "OK", 1: "WARNING", 2: "CRITICAL", 3: "UNKNOWN"}
LOGLEVELS = {
    "none": 0,
    "info": 20,
    "warning": 30,
    "error": 40,
    "debug": 10
}
