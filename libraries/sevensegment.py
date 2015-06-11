#!/usr/bin/python

import sys
import logging

from tools import KAPCOMLog

# Logging
_log = KAPCOMLog("SevenSegment", logging.WARN)
log = _log.log


class SevenSegment(object):
    formats = [
        "default"
    ]

    def __init__(self, name, api, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self.device = None
        self._arduino = None

        self.name = name
        self.api = api

        # Pre-set extra attributes
        self._type = "default"
        self._length = 8
        self._offset = 0
        self._decimals = 3
        self._pad = " "

        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])

        # Set ephemeral values
        self.value = "-" * self._length
        self._lastvalue = "-" * self._length

        # Run initial update
        self.update()

    @staticmethod
    def _color(character, color):
        try:
            from termcolor import colored

            return colored(character, color)
        except ImportError:
            return character

    def attach(self, arduino, device):
        self._arduino = arduino
        self.device = device

    def detatch(self):
        self._arduino = None
        self.device = None

    def set(self, value):
        log.debug("Setting seven-segment " + self.name + " " + str(value))

        self._lastvalue = self.value

        if isinstance(value, str):
            self.value = float(value)
        else:
            self.value = int(value)

        self.format()
        self.update()

    def update(self):
        self.write()

    def printout(self):
        print "Display " + self.name
        print str(self)

    def __str__(self):
        return "[" + self._color(self.value, "green") + "]"

    def format(self):
        # Take the value passed and format it for the 8 digit seven-segment display

        # Counter for exponents when using scientific notation
        exponent = 0

        # Break the value into integer and decimal portions
        value = '{0:f}'.format(self.value)
        integer = value[:value.index('.')]
        decimal = value[value.index('.') + 1:]

        if len(integer) > self._length:
            significant = len(integer)

            # print "Value:       " + str(self.value)
            # print "Exponent:    " + str(exponent)
            # print "New Value:   " + value
            # print "Significant: " + str(significant)
            # print "Calculating..."

            while significant + len(str(exponent)) + 1 > self._length:
                exponent += 3
                significant = len(integer) - exponent

            # print "Exponent:    " + str(exponent)
            # print "Significant: " + str(significant)

            formatted = value[:significant] + "E" + str(exponent)

            # print "Formatted:   " + formatted
            decimals = self._length - len(formatted)
            # print "Decimals:    " + str(decimals)
            if decimals > 0:
                formatted = value[:significant] + "." + value[significant:significant + decimals] + "E" + str(exponent)

                # print "Reformatted: " + formatted

        elif len(integer) < self._length:
            # Fewer integers than can be displayed
            # Attempt to fill with decimals

            # Truncate the decimals to fit on the display
            decimal = decimal[:self._length - len(integer)]

            # Truncate the decimals according to maximum decimal length
            if len(decimal) > self._decimals:
                decimal = decimal[:self._decimals]

            # Create formatted string
            formatted = integer + "." + decimal

        else:
            # Integers fill display
            formatted = integer + "."

        # Pad string if it's too short
        if len(formatted.replace(".", "")) < self._length:
            for i in range(0, self._length - len(formatted.replace(".", ""))):
                formatted = self._pad + formatted

        # Final check for string length
        if len(formatted.replace(".", "")) != self._length:
            # Print a debug message
            log.warn("Something went wrong while formatting: " + str(self.value) + " >> " + formatted)

            # Set the display to dashes
            formatted = "-" * self._length

        self.value = formatted

    def write(self):
        if self.value != self._lastvalue:
            self._arduino.display_write(self.device, self.value)


# #####################################
# ########## Testing Methods ##########
# #####################################


def main():
    from arduino import Arduino
    from tools import breakpoint

    a = Arduino("Test")
    d = SevenSegment(a, "Test", "test")

    import time

    value = .00000012345678

    for i in range(0, 20):
        d.set(value)

        print str(d)

        value *= 10
        time.sleep(1)

        breakpoint()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
        # except:
        # sys.exit(0)
