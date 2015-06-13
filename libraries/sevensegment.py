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
        self.arduino = None

        self.name = name
        self.api = api

        # Pre-set extra attributes
        self.type = "default"
        self.length = 8
        self.offset = 0
        self.decimals = 3
        self.pad = " "

        # Override defaults with passed values
        if options:
            for key in options:
                print "'" + key + "'"
                setattr(self, key, options[key])

        # Set ephemeral values
        self.value = "-" * self.length
        self._lastvalue = "-" * self.length

        # Run initial update
        self.update()

    def attach(self, arduino, device):
        self.arduino = arduino
        self.device = device

    def detatch(self):
        self.arduino = None
        self.device = None

    def is_attached(self):
        if self.arduino is not None and self.device is not None:
            return True
        else:
            return False

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
        return "[" + self.value + "]"

    def format(self):
        # Take the value passed and format it for the 8 digit seven-segment display

        # Counter for exponents when using scientific notation
        exponent = 0

        # Break the value into integer and decimal portions
        value = '{0:f}'.format(self.value)
        integer = value[:value.index('.')]
        decimal = value[value.index('.') + 1:]

        if len(integer) > self.length:
            significant = len(integer)

            # print "Value:       " + str(self.value)
            # print "Exponent:    " + str(exponent)
            # print "New Value:   " + value
            # print "Significant: " + str(significant)
            # print "Calculating..."

            while significant + len(str(exponent)) + 1 > self.length:
                exponent += 3
                significant = len(integer) - exponent

            # print "Exponent:    " + str(exponent)
            # print "Significant: " + str(significant)

            formatted = value[:significant] + "E" + str(exponent)

            # print "Formatted:   " + formatted
            decimals = self.length - len(formatted)
            # print "Decimals:    " + str(decimals)
            if decimals > 0:
                formatted = value[:significant] + "." + value[significant:significant + decimals] + "E" + str(exponent)

                # print "Reformatted: " + formatted

        elif len(integer) < self.length:
            # Fewer integers than can be displayed
            # Attempt to fill with decimals

            # Truncate the decimals to fit on the display
            decimal = decimal[:self.length - len(integer)]

            # Truncate the decimals according to maximum decimal length
            if len(decimal) > self.decimals:
                decimal = decimal[:self.decimals]

            # Create formatted string
            formatted = integer + "." + decimal

        else:
            # Integers fill display
            formatted = integer + "."

        # Pad string if it's too short
        if len(formatted.replace(".", "")) < self.length:
            for i in range(0, self.length - len(formatted.replace(".", ""))):
                formatted = "{}{}".format(self.pad, formatted)

        # Final check for string length
        if len(formatted.replace(".", "")) != self.length:
            # Print a debug message
            log.warn("Something went wrong while formatting: " + str(self.value) + " >> " + formatted)

            # Set the display to dashes
            formatted = "-" * self.length

        self.value = formatted

    def write(self):
        if self.value != self._lastvalue and self.arduino is not None and self.arduino.connected:
            self.arduino.display_write(self.device, self.value)

    def get_data(self):
        if self.is_attached():
            data = {
                "Name": self.name,
                "API": self.api,
                "Type": "SevenSegment",
                "Format": self.type,
                "Value": self.value,
                "Arduino": self.arduino.name,
                "Device": self.device,
                "Length": self.length,
                "Decimals": self.decimals,
                "Pad": self.pad
            }
        else:
            data = {
                "Name": self.name,
                "API": self.api,
                "Type": "SevenSegment",
                "Format": self.type,
                "Value": self.value,
                "Arduino": "None",
                "Device": "None",
                "Length": self.length,
                "Decimals": self.decimals,
                "Pad": self.pad
            }

        return data