#!/usr/bin/python

from abc import ABCMeta, abstractmethod
from datetime import datetime
import sys
import logging
import pyautogui

from tools import KAPCOMLog

# Logging
_log = KAPCOMLog("Pin", logging.WARN)
log = _log.log


class _Pin(object):
    __metaclass__ = ABCMeta

    # Core Class Members
    # name
    # api
    # pin
    # value
    # arduino
    # _format
    # _invert
    # _cooldown
    # _lastupdate
    # _lastvalue

    # Optional Class Members
    # _max

    def __init__(self, arduino, name, api, pin, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self.arduino = arduino
        self.name = name
        self.api = api
        self.pin = pin

        # Pre-set extra attributes
        self.cooldown = 500
        self.invert = False
        self.format = "value"
        self.max = 1024
        self.deadzone = 0
        self.key = ""

        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])

        # Set ephemeral values
        self.value = 0
        self._lastvalue = self.value
        self._lastupdate = datetime.now()

    @abstractmethod
    def _action(self, value=None):
        log.critical("Abstract method act() called for " + self.name + "!")

    def get(self):
        self.update()
        return self.value

    def push(self, value):
        """Attempts to push the selected value and update"""
        if value in ["1", "True", True]:
            value = 1
        if value in ["0", "False", False]:
            value = 0

        return self.update(value)

    def set(self, value):
        """Set the value and update"""
        if value in ["1", "True", True]:
            value = 1
        if value in ["0", "False", False]:
            value = 0

        self.update(value)

    def update(self, value=None):
        """Check cooldown timer and act"""
        # Check if cooldown has expired
        delta = self._lastupdate - datetime.now()
        if (delta.total_seconds() * 1000) > self.cooldown:
            log.debug("Cooldown not reached")
            return
        # Update counter
        self._lastupdate = datetime.now()
        # Perform action described in individual class
        self._action(value)

    def changed(self):
        """Check if value has changed since last check"""
        changed = (self._lastvalue != self.value)
        self._lastvalue = self.value
        return changed

    def printout(self):
        print "{0} ({1})={2}".format(self.name, self.api, self.value)

    def __str__(self):
        # Define lambdas for selecting value based on format
        displays = {
            "value": lambda x: str(x),
            "toggle": lambda x: (None, "")[x],
            "truefalse": lambda x: ("True", "False")[x],
            "true": lambda x: ("True", "")[x],
            "false": lambda x: ("", "False")[x],
            "zero": lambda x: ("0", "")[x],
            "one": lambda x: ("1", "")[x],
            "floatpoint": lambda x: str(float(x) / self.max),
            "percent": lambda x: str(float(x) / self.max * 100),
            "key": lambda x: pyautogui.press(self.key) if x == 1 else False
        }

        # Try to run the lambda specified by _format
        f = displays.get(self.format)
        if f is not None:
            return f(self.value)
        else:
            log.warn('Format not found "{0}"'.format(self.format))
            return ""


class AnalogIn(_Pin):
    def __init__(self, arduino, name, api, pin, options=None):
        super(AnalogIn, self).__init__(arduino, name, api, pin, options)
        self.arduino.pin_mode(self.pin, "INPUT_PULLUP")

    def _action(self, value=None):
        """If no value is passed, read"""
        if value is not None:
            log.warn("Value sent while updating an AnalogIn object")
            return None

        return self.read()

    def set_max(self, new):
        """Set the maximum value"""
        self.max = new

    def get_float(self):
        """Update the hardware and return latest value"""
        self.update()
        return float(self.value) / self.max

    def changed(self):
        """Check if value has changed significantly since last check"""
        changed = float(self._lastvalue - self.value) / self.max * 100

        if abs(changed) > 1:
            self._lastvalue = self.value
            return True
        else:
            return False

    def read(self):
        """Read from hardware"""
        self.value = int(self.arduino.analog_read(self.pin))

        if self.invert:
            self.value = self.max - self.value

        if self.value < self.max * self.deadzone:
            self.value = 0
        elif self.value > self.max * (1 - self.deadzone):
            self.value = self.max

        return self.value


class AnalogOut(_Pin):
    def __init__(self, arduino, name, api, pin, options=None):
        super(AnalogOut, self).__init__(arduino, name, api, pin, options)
        self.arduino.pin_mode(self.pin, "OUTPUT")
        self.cooldown = 0

    def _action(self, value=None):
        """Write the value"""
        if value is None:
            log.warn("No value sent while updating an AnalogOut object")
            return

        self.write(value)

    def set_max(self, new):
        """Set the maximum value"""
        self.max = new

    def get_float(self):
        """Update the hardware and return latest value"""
        self.update()
        return float(self.value) / self.max

    def changed(self):
        """Check if value has changed significantly since last check"""
        changed = float(self._lastvalue - self.value) / self.max * 100

        if abs(changed) > 1:
            self._lastvalue = self.value
            return True
        else:
            return False

    def write(self, value):
        """Write to hardware"""
        if value:
            self.value = int(value)

            if self.invert:
                self.value = self.max - self.value

            self.arduino.analog_write(self.pin, self.value)


class DigitalIn(_Pin):
    def __init__(self, arduino, name, api, pin, options=None):
        super(DigitalIn, self).__init__(arduino, name, api, pin, options)
        self.arduino.pin_mode(self.pin, "INPUT_PULLUP")

    def _action(self, value=None):
        """If no value is passed, read"""
        if value is not None:
            log.warn("Value sent while updating an DigitalIn object")
            return None

        return self.read()

    def read(self):
        """Read from hardware"""
        self.value = int(self.arduino.digital_read(self.pin))

        if self.invert:
            if self.value == 0:
                self.value = 1
            elif self.value == 1:
                self.value = 0
            else:
                log.error("Unexpected value")

        return self.value


class DigitalOut(_Pin):
    def __init__(self, arduino, name, api, pin, options=None):
        super(DigitalOut, self).__init__(arduino, name, api, pin, options)
        self.arduino.pin_mode(self.pin, "OUTPUT")
        self.cooldown = 0

    def _action(self, value=None):
        """Write the value"""
        if value is None:
            log.warn("No value sent while updating an DigitalOut object")
            return

        self.write(value)

    def write(self, value):
        """Write to hardware"""

        if value is not None:
            try:
                self.value = int(value)
            except ValueError:
                print "Unparsable value: " + value

            if self.invert:
                if self.value == 0:
                    self.value = 1
                elif self.value == 1:
                    self.value = 0
                else:
                    log.error("Unexpected value: " + value)

            self.arduino.digital_write(self.pin, self.value)


# #####################################
# ########## Testing Methods ##########
# #####################################


def main():
    from arduino import Arduino
    from tools import breakpoint

    a = Arduino("Test")

    ai = AnalogIn(a, "Throttle", "throttle", 0xA8)
    ao = AnalogOut(a, "Dimmer", "dimmer", 0x08)
    di = DigitalIn(a, "SAS", "sas", 0x0A)
    do = DigitalOut(a, "SAS Status", "sas_status", 0x0B)

    ai.update()
    ao.update(256)
    di.update()
    do.update(1)

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