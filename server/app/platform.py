__author__ = 'drobisch'

import platform
import re

UNKNOWN          = "UNKOWN"
RASPBERRY_PI     = "RASPBERRY_PI"
RASPBERRY_PI_2   = "RASPBERRY_PI2"


def platform_getType():
    """Detect the running platform"""

    # read the cpuinfo#
    try:
        with open('/proc/cpuinfo', 'r') as readfile:
            cpuinfo = readfile.read()

        match = re.search('^Hardware\s+:\s+(\w+)$', cpuinfo,
                          flags=re.MULTILINE | re.IGNORECASE)
        if not match:
            return UNKNOWN
        if match.group(1) == 'BCM2708':
            RASPBERRY_PI
            return RASPBERRY_PI
        if match.group(1) == 'BCM2709':
            RASPBERRY_PI_2
            return RASPBERRY_PI_2
    except:
        return UNKNOWN