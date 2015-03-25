#!/usr/bin/python

from pin import pin
from arduino import arduino

class mod(object):
    def __init__(self, arduino, name, api, modifier, indicator, button, options=None):
        """Initialize modifier with parameters"""
        
        # Set core attributes
        self.mod            = digitalIn(arduino, name + " Modifier", "", modifier)
        self.indicator      = digitalOut(arduino, name + " Indicator", "", indicator)
        self.button         = digitalIn(arduino, name + " Button", "", button)
        
        self.name           =   name
        self.api            =   api
        
        # Pre-set extra attributes
        self._format        =   "value"
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        self.update()
        self.value          =   0
        # Not sure if I need this...
        self._lastvalue     =   self.value
        
    def get(self):
        self.update()
        return self.value
        
    def toString(self):
        # Define lambdas for selecting value based on format
        value       = lambda x: str(x)
        toggle      = lambda x: (None, "")[x]
        truefalse   = lambda x: ("True", "False")[x]
        true        = lambda x: ("True", "")[x]
        false       = lambda x: ("", "False")[x]
        zero        = lambda x: ("0", "")[x]
        one         = lambda x: ("1", "")[x]
        
        # Define function for pressing a key
        def key(x):
            """Press a key"""
            keyCommand = "osascript -e 'tell application \"Kerbal Space Program\" to keystroke \""+self.key+"\"'"
            os.system(keyCommand)
        
        # Try to run the lambda/function specified by __format
        try:
            func = getattr(modulename, self._format)
        except AttributeError:
            print 'Format not found "%s" (%s)' % (self._format, arg)
        else:
            self._format(self.value)

    def update(self):
        isLocked = self.mod.get()
        self.indicator.set(isLocked)
        
        if isLocked is 0:
            self.value = 0
        else:
            self.value = button.get()
        
    def changed(self):
        isUpdated = self._lastvalue != self.value
        self._lastvalue = self.value
        return isUpdated

    def printout(self):
        print  "{0} ({1})={2}".format(self.name, self.api, self.value)
        self.mod.printout()
        self.indicator.printout()
        self.button.printout()


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