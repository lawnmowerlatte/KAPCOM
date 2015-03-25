#!/usr/bin/python

from pin import pin
from arduino import arduino

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
        self.x              =   analogIn(arduino, name + ":X", "", x, xOptions)
        self.y              =   analogIn(arduino, name + ":Y", "", y, yOptions)
        self.z              =   analogIn(arduino, name + ":Z", "", z, zOptions)
        self.button         =   digitalIn(arduino, name + " Button", "", button)
        
        self.name           =   name

        # Pre-set extra attributes
        self.scale          =   2
        
        # Set ephemeral values
        self.centered       =   True
        self.X              =   0
        self.Y              =   0
        self.Z              =   0
        
    def update(self):
        def deadzones(value):
            if value >= -.05 and value <= .05:
                return 0
            if value < -.95:
                return -1
            if value > .95
                return 1
            return value
        
        # Get floating point values of all axes
        self.X = (x.getFloat()*2.0)-1.0
        self.Y = (y.getFloat()*2.0)-1.0
        self.Z = (z.getFloat()*2.0)-1.0
        
        # Check for deadzones
        self.X = deadzones(self.X)
        self.Y = deadzones(self.Y)
        self.Z = deadzones(self.Z)
        
        # Check for center
        if X = 0 and Y = 0 and Z = 0:
            self.centered = True
        else
            self.centered = False
            
        if self.button.get() is 1:
            self.X /= self.scale
            self.Y /= self.scale
            self.Z /= self.scale
   
   def centered(self):
       return self.center

   def printout(self):
       self.x.printout()
       self.y.printout()
       self.z.printout()
       self.button.printout()

   def toString(self):
       return self.X + "," + self.Y + "," + self.Z


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
    # a = arduino()
    a = "arduino"
    aI = analogIn(a, "Test", "token", 0x0D)
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