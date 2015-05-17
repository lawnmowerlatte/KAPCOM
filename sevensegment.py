#!/usr/bin/python

import sys
import logging
import pyautogui
from arduino import Arduino

# Logging
_name = "SevenSegment"
_debug = logging.DEBUG

log = logging.getLogger(_name)
if not len(log.handlers):
    log.setLevel(_debug)

    longFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-10.10s]  %(message)s")
    shortFormatter = logging.Formatter("[%(levelname)-8.8s]  %(message)s")

    fileHandler = logging.FileHandler("logs/{0}/{1}.log".format("./", _name))
    fileHandler.setFormatter(longFormatter)
    log.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(shortFormatter)
    log.addHandler(consoleHandler)


class SevenSegment(object):
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

    def _color(self, character, color):
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
        print self.toString()

    def toString(self):
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
            self._arduino.displayWrite(self.device, self.value)


# #####################################
# ########## Testing Methods ##########
# #####################################


def breakpoint():
    """Python debug breakpoint."""

    from code import InteractiveConsole
    from inspect import currentframe

    try:
        import readline
    except ImportError:
        pass

    caller = currentframe().f_back

    env = {}
    env.update(caller.f_globals)
    env.update(caller.f_locals)

    shell = InteractiveConsole(env)
    shell.interact(
        '* Break: {} ::: Line {}\n'
        '* Continue with Ctrl+D...'.format(
            caller.f_code.co_filename, caller.f_lineno
        )
    )


def main():
    a = Arduino()
    d0 = SevenSegment(a, "Test", "test", 0)
    d1 = SevenSegment(a, "Test", "test", 1)
    d2 = SevenSegment(a, "Test", "test", 2)
    d3 = SevenSegment(a, "Test", "test", 3)
    d4 = SevenSegment(a, "Test", "test", 4)

    import time

    value = .00000012345678

    for i in range(0, 20):
        d0.set(value)
        d1.set(value)
        d2.set(value)
        d3.set(value)
        d4.set(value)

        print d0.toString()

        value *= 10
        time.sleep(1)

        # breakpoint()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
        # except:
        # sys.exit(0)
