#!/usr/bin/python

import sys
from datetime import datetime
import pyautogui
from pin import DigitalIn, DigitalOut
from arduino import Arduino
from tools import *

# Logging
_log = KAPCOMLog("Mod", logging.WARN)
log = _log.log


class Mod(object):
    def __init__(self, arduino, name, api, modifier, indicator, button, options=None):
        """Initialize modifier with parameters"""

        # Set core attributes
        self.mod = DigitalIn(arduino, name + " Modifier", "", modifier, options.get('modifier'))
        self.indicator = DigitalOut(arduino, name + " Indicator", "", indicator, options.get('indicator'))
        self.button = DigitalIn(arduino, name + " Button", "", button, options.get('button'))

        self.name = name
        self.api = api

        # Pre-set extra attributes
        self._format = "value"
        self._initial = 0

        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])

        # Set ephemeral values
        self.value = self._initial
        self._lastvalue = self.value
        self._lastupdate = datetime.now()

        # Run initial update
        self.update()

    def get(self):
        self.update()
        return self.value

    def __str__(self):
        # Define lambdas for selecting value based on format
        value = lambda x: str(x)
        toggle = lambda x: (None, "")[x]
        truefalse = lambda x: ("True", "False")[x]
        true = lambda x: ("True", "")[x]
        false = lambda x: ("", "False")[x]
        zero = lambda x: ("0", "")[x]
        one = lambda x: ("1", "")[x]
        key = lambda x: pyautogui.press(self._key) if x == 1 else False

        # Try to run the lambda specified by _format
        f = locals().get(self._format)
        try:
            return f(self.value)
        except AttributeError:
            print 'Format not found "%s"' % self._format

    def update(self):
        is_locked = self.mod.get()
        self.indicator.set(is_locked)

        if int(is_locked) is 0:
            self.value = 0
        else:
            self.value = self.button.get()

    def changed(self):
        is_updated = self._lastvalue != self.value
        self._lastvalue = self.value
        return is_updated

    def printout(self):
        print "{0} ({1})={2}".format(self.name, self.api, self.value)
        self.mod.printout()
        self.indicator.printout()
        self.button.printout()


# #####################################
# ########## Testing Methods ##########
# #####################################


def main():
    a = Arduino("Test")

    abort = Mod(a, "Abort", "abort", 0xA9, 0xAB, 0xAA)
    stage = Mod(a, "Stage", "stage", 0xAC, 0xAE, 0xAD)

    import time

    while False:
        abort.update()
        stage.update()
        abort.printout()
        abort.printout()

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