#!/usr/bin/python

from pin import *
from arduino import Arduino

class joy(object):
    
    def __init__(self, arduino, name, x, y, z, button, options=None):
        allOptions = {'format':'floatpoint'}
        
        try:
            buttonOptions = {'format':'value'}
            buttonInvert = options['invertButton']
            buttonOptions['invert'] = buttonInvert
        except:
            pass
        try:
            xOptions = allOptions.copy()
            xInvert = options['invertX']
            xOptions['invert'] = xInvert
        except:
            pass
        try:
            yOptions = allOptions.copy()
            yInvert = options['invertY']
            yOptions['invert'] = yInvert
        except:
            pass
        try:
            zOptions = allOptions.copy()
            zInvert = options['invertZ']
            zOptions['invert'] = zInvert
        except:
            pass
        
        # Set core attributes
        self.x              =   AnalogIn(arduino, name + ":X", "", x, xOptions)
        self.y              =   AnalogIn(arduino, name + ":Y", "", y, yOptions)
        self.z              =   AnalogIn(arduino, name + ":Z", "", z, zOptions)
        self.button         =   DigitalIn(arduino, name + " Button", "", button)
        
        self.name           =   name

        # Pre-set extra attributes
        self.scale          =   2
        
        # Set ephemeral values
        self.centered       =   True
        self.X              =   0
        self.Y              =   0
        self.Z              =   0
        
        # Run initial update
        self.update()
        
    def update(self):
        def deadzones(value, deadzone=.05):
            if value >= -1 * deadzone and value <= deadzone:
                return 0
            if value < -1 + deadzone:
                return -1
            if value > 1 - deadzone:
                return 1
            return value
        
        # Get floating point values of all axes
        self.X = (self.x.get_float()*2.0)-1.0
        self.Y = (self.y.get_float()*2.0)-1.0
        self.Z = (self.z.get_float()*2.0)-1.0
        
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
            self.X = (self.X*1.0)/self.scale
            self.Y = (self.Y*1.0)/self.scale
            self.Z = (self.Z*1.0)/self.scale
   
    def centered(self):
        return self.center

    def printout(self):
        print self.name + ": " + self.toString()
        self.x.printout()
        self.y.printout()
        self.z.printout()
        self.button.printout()

    def toString(self):
        return str(self.X) + "," + str(self.Y) + "," + str(self.Z)


# #####################################
# ########## Testing Methods ##########
# #####################################


def breakpoint():
    """Python debug breakpoint."""
    
    from code import InteractiveConsole
    from inspect import currentframe
    try:
        import readline # noqa
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
    
    j0 = joy(a, "J0", 0xA0, 0xA1, 0xA2, 0xA3)
    j1 = joy(a, "J0", 0xA4, 0xA5, 0xA6, 0xA7)
    
    import time
    while True:
        j0.update()
        j1.update()
        print j0.toString() + "," + j1.toString()
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
    #     sys.exit(0)