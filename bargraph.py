#!/usr/bin/python

from arduino import arduino
from termcolor import colored

class bargraph(object):
    
    def __init__(self, arduino, name, api, device, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self._arduino       =   arduino
        self.name           =   name
        self.api            =   api
        self.device         =   device
        
        # Pre-set extra attributes
        self._type          =   "default"
        self._max           =   100
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Set ephemeral values
        self.value        =   0
        self.red          = [ False, False, False, False, False, False,
                              False, False, False, False, False, False,
                              False, False, False, False, False, False,
                              False, False, False, False, False, False, ]
        self.green        = [ False, False, False, False, False, False,
                              False, False, False, False, False, False,
                              False, False, False, False, False, False,
                              False, False, False, False, False, False, ]
        
        for i in range(self._max, 0):
            self.set(i)
        
        # Run initial update
        self.update()
        
    def set(self, value):
        self.value = value
        self.update()
        
    def setMax(self, newMax):
        self._max = newMax

    def update(self):
        self.format()
        self.write()
        
    def printout(self):
        print "Bargraph " + self.name + " (Type = " + self._type + ")"
        print self.toString()
        
    def toString(self):
        color   = "black"
        bar     = "["
        char    = "|"
        
        for i in range(0, 24):
            if self.red[i] and self.green[i]:
                char    =   colored(char, "yellow")
            elif self.red[i]:
                char    =   colored(char, "red")
            elif self.green[i]:
                char    =   colored(char, "green")
            else:
                char    =   " "
            
            bar+=char
        
        bar += "]"
        return  bar
        
    def format(self):
        def clear():
            for i in range(0, 24):
                self.red[i]     =   False
                self.green[i]   =   False
        
        def default():
            percent = float(self.value) * 100 / self._max;
            
            for i in range(0, min(24, int(24*percent/100))):
                if percent > 50:
                    self.green[i]   =   True
                elif percent > 20:
                    self.green[i]   =   True
                    self.red[i]     =   True
                if percent <= 20:
                    self.green[i]   =   False
                    self.red[i]     =   True
        
        clear()
        f = locals().get(self._type)
        if not f:
            debug("Unknown type: " + self._type)
        
        f()
        
        
            
            
    def write(self):
        self._arduino.bargraphWrite(self.device, self.red, self.green)


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
    
    bar0 = bargraph(a, "Test", "test", 0)
    bar1 = bargraph(a, "Test", "test", 1)
    bar2 = bargraph(a, "Test", "test", 2)
    bar3 = bargraph(a, "Test", "test", 3)
    # bar4 = bargraph(a, "Test", "test", 4)
    
    bar0.update()
    bar1.update()
    bar2.update()
    bar3.update()
    # bar4.update()
    
    bar0.printout()
    
    import time
    
    for i in range(0, 100):
        bar0.set(i)
        bar1.set(i)
        bar2.set(i)
        bar3.set(i)
        # bar4.set(i)
        
        bar0.printout()
        
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
