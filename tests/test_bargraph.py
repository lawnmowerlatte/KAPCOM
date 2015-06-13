#!/usr/bin/python

import os
import sys

sys.path.append(os.getcwd() + "/libraries")

from arduino import Arduino
from bargraph import Bargraph


def test_init():
    a = Arduino("Test Arduino")
    bar = Bargraph("Test Bargraph", "Test api")
    assert bar.name == "Test Bargraph"
    assert bar.api == "Test api"
    assert bar.arduino is None

    bar.attach(a, 0)
    assert bar.arduino is not None
    assert bar.arduino.name == "Test Arduino"


def test_set():
    a = Arduino("Test Arduino")
    bar = Bargraph("Test Bargraph", "Test api")
    bar.attach(a, 0)

    bar.set(100, 100)
    assert bar.value == 100
    assert bar.max == 100


def test_str(capsys):
    a = Arduino("Test Arduino")
    bar = Bargraph("Test Bargraph", "Test api", {"type": "green"})
    bar.attach(a, 0)

    bar.set(24, 24)
    print str(bar)
    out, err = capsys.readouterr()
    assert out == "[GGGGGGGGGGGGGGGGGGGGGGGG]\n"

    bar.set(12, 24)
    print str(bar)
    out, err = capsys.readouterr()
    assert out == "[GGGGGGGGGGGG            ]\n"

    bar.set(6, 24)
    print str(bar)
    out, err = capsys.readouterr()
    assert out == "[GGGGGG                  ]\n"

    bar.set(0, 24)
    print str(bar)
    out, err = capsys.readouterr()
    assert out == "[                        ]\n"

    bar.set(0, 0)
    print str(bar)
    out, err = capsys.readouterr()
    assert out == "[                        ]\n"