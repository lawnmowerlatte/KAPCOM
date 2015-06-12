#!/usr/bin/python

import os
import sys

sys.path.append(os.getcwd() + "/libraries")

from arduino import Arduino


def test_init():
    a = Arduino("Test Device", "1e322429-bff8-4773-8d1b-38f13612ab33", None, 115200, 2, None, False)
    assert a.name == "Test Device"