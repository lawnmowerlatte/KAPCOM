#!/usr/bin/python

import sys
import logging

from pin import AnalogIn, DigitalIn
from tools import KAPCOMLog

# Logging
_log = KAPCOMLog("Joy", logging.WARN)
log = _log.log


class Joy(object):
    def __init__(self, arduino, name, api, x, y, z, button, options=None):
        all_options = {'format': 'floatpoint'}
        button_options = {'format': 'value'}

        try:
            invert_button = options['invertButton']
            button_options['invert'] = invert_button
        except (KeyError, TypeError):
            button_options = None

        try:
            x_options = all_options.copy()
            invert_x = options['invertX']
            x_options['invert'] = invert_x
        except (KeyError, TypeError):
            x_options = None

        try:
            y_options = all_options.copy()
            invert_y = options['invertY']
            y_options['invert'] = invert_y
        except (KeyError, TypeError):
            y_options = None

        try:
            z_options = all_options.copy()
            invert_z = options['invertZ']
            z_options['invert'] = invert_z
        except (KeyError, TypeError):
            z_options = None

        # Set core attributes
        self.x = AnalogIn({arduino, name + ":X", "", x, x_options})
        self.y = AnalogIn({arduino, name + ":Y", "", y, y_options})
        self.z = AnalogIn({arduino, name + ":Z", "", z, z_options})
        self.button = DigitalIn({arduino, name + " Button", "", button, button_options})

        self.name = name
        self.api = api

        # Pre-set extra attributes
        self.scale = 2

        # Set ephemeral values
        self.centered = True
        self.X = 0
        self.Y = 0
        self.Z = 0

        # Run initial update
        self.update()

    def update(self):
        def deadzones(value, deadzone=.05):
            if deadzone >= value >= -1 * deadzone:
                return 0
            if value < -1 + deadzone:
                return -1
            if value > 1 - deadzone:
                return 1
            return value

        # Get floating point values of all axes
        self.X = (self.x.get_float() * 2.0) - 1.0
        self.Y = (self.y.get_float() * 2.0) - 1.0
        self.Z = (self.z.get_float() * 2.0) - 1.0

        # Check for deadzones
        self.X = deadzones(self.X)
        self.Y = deadzones(self.Y)
        self.Z = deadzones(self.Z, .1)

        # Check for center
        if self.X == 0 and self.Y == 0 and self.Z == 0:
            self.centered = True
        else:
            self.centered = False

        if self.button.get() is 0:
            self.X = (self.X * 1.0) / self.scale
            self.Y = (self.Y * 1.0) / self.scale
            self.Z = (self.Z * 1.0) / self.scale

    def printout(self):
        print self.name + ": " + str(self)
        self.x.printout()
        self.y.printout()
        self.z.printout()
        self.button.printout()

    def __str__(self):
        return str(self.X) + "," + str(self.Y) + "," + str(self.Z)


# #####################################
# ########## Testing Methods ##########
# #####################################


def main():
    from arduino import Arduino
    from tools import breakpoint

    a = Arduino("Test")

    j0 = Joy(a, "J0", "", 0xA0, 0xA1, 0xA2, 0xA3)
    j1 = Joy(a, "J0", "", 0xA4, 0xA5, 0xA6, 0xA7)

    import time

    while True:
        j0.update()
        j1.update()
        print str(j0) + "," + str(j1)
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