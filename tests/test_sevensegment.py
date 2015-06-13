#!/usr/bin/python

import os
import sys

sys.path.append(os.getcwd() + "/libraries")

from arduino import Arduino
from sevensegment import SevenSegment


def test_init():
    a = Arduino("Test Arduino")
    sev = SevenSegment("Test SevenSegment", "Test api")
    assert sev.name == "Test SevenSegment"
    assert sev.api == "Test api"
    assert sev.arduino == None

    sev.attach(a, 0)
    assert sev.arduino is not None
    assert sev.arduino.name == "Test Arduino"


def test_formatter(capsys):
    a = Arduino("Test Arduino")
    sev = SevenSegment("Test SevenSegment", "Test api")
    sev.attach(a, 0)

    value = .00000012345678
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.000]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.000]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.000]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.000]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.001]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.012]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    0.123]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[    1.234]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[   12.345]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[  123.456]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[ 1234.567]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[12345.678]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[123456.78]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[1234567.8]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[12345678.]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[123456E3]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[1234.56E6]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[12345.6E6]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[123456E6]\n"

    value *= 10
    sev.set(str(value))
    print str(sev)
    out, err = capsys.readouterr()
    assert out == "[1234.56E9]\n"

