#!/usr/bin/python

import os
import sys

sys.path.append(os.getcwd() + "/libraries")

from arduino import Arduino
from pin import DigitalIn, DigitalOut, AnalogIn, AnalogOut


def test_analogin_init():
    a = Arduino("Test Arduino")

    pin = AnalogIn(a, "Test Pin", "Test api", 0)

    assert pin.name == "Test Pin"
    assert pin.api == "Test api"
    assert pin.arduino.name == "Test Arduino"


def test_analogout_init():
    a = Arduino("Test Arduino")

    pin = AnalogOut(a, "Test Pin", "Test api", 0)

    assert pin.name == "Test Pin"
    assert pin.api == "Test api"
    assert pin.arduino.name == "Test Arduino"


def test_digitalin_init():
    a = Arduino("Test Arduino")

    pin = DigitalIn(a, "Test Pin", "Test api", 0)

    assert pin.name == "Test Pin"
    assert pin.api == "Test api"
    assert pin.arduino.name == "Test Arduino"


def test_digitalout_init():
    a = Arduino("Test Arduino")

    pin = DigitalOut(a, "Test Pin", "Test api", 0)

    assert pin.name == "Test Pin"
    assert pin.api == "Test api"
    assert pin.arduino.name == "Test Arduino"


def test_analogin_get():
    a = Arduino("Test Arduino")

    pin = AnalogIn(a, "Test Pin", "Test api", 0)

    pin.value = 500
    assert pin.get() == 500
