#!/usr/bin/python

import os
import sys

sys.path.append(os.getcwd() + "/libraries")

from arduino import Arduino
from mod import Mod

def test_init():
    a = Arduino("Test Arduino")

    mod = Mod(a, "Test Mod", "Test api", 0xA9, 0xAB, 0xAA)

    assert mod.name == "Test Mod"
    assert mod.api == "Test api"
    assert mod.mod.arduino.name == "Test Arduino"
    assert mod.indicator.arduino.name == "Test Arduino"
    assert mod.button.arduino.name == "Test Arduino"
