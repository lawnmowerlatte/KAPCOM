#!/usr/bin/python

from pin import *
from arduino import arduino

class mod(object):
    def __init__(self, arduino, name, api, pin, options=None):
        """Initialize modifier with parameters"""
        
        # Remap pins from array
        modifier    =   pin[0]
        indicator   =   pin[1]
        button      =   pin[2]
        
        try:
            modifierOptions     =   options['modifier']
        except:
            modifierOptions     =   None
        
        try:
            indicatorOptions    =   options['indicator']
        except:
            indicatorOptions    =   None
            
        try:
            buttonOptions       =   options['button']
        except:
            buttonOptions       =   None
        
        # Set core attributes
        self.mod            = digitalIn(arduino, name + " Modifier", "", modifier, modifierOptions)
        self.indicator      = digitalOut(arduino, name + " Indicator", "", indicator, indicatorOptions)
        self.button         = digitalIn(arduino, name + " Button", "", button, buttonOptions)
        
        self.name           =   name
        self.api            =   api
        
        # Pre-set extra attributes
        self._format        =   "value"
        self._initial       =   0
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Set ephemeral values
        self.value          =   self._initial
        self._lastvalue     =   self.value
        self._lastupdate    =   datetime.now()
        
        # Run initial update
        self.update()
        
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
        
        # Try to run the lambda/function specified by _format
        f = locals().get(self._format)
        try:
            return f(self.value)
        except AttributeError:
            print 'Format not found "%s"' % (self._format)

    def update(self):
        isLocked = self.mod.get()
        self.indicator.set(isLocked)
        
        if int(isLocked) is 0:
            self.value = 0
        else:
            self.value = self.button.get()
        
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
    a = arduino()
    
    abort = mod(a, "Abort", "abort", 0xA9, 0xAB, 0xAA)
    stage = mod(a, "Stage", "stage", 0xAC, 0xAE, 0xAD)
    
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
    #     sys.exit(0)