#!/usr/bin/python

from datetime import datetime
from arduino import arduino

class bargraph(object):
    
    def __init__(self, arduino, name, api, device, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self._arduino       =   arduino
        self.name           =   name
        self.api            =   api
        self.device         =   device
        
        # Pre-set extra attributes
        self._type          =   "delta"
        self._max           =   100
        self._showdelta     =   30*1000
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Set ephemeral values
        self.value          =   0
        self._lastvalue     =   0
        
        self._lastupdate    =   datetime.now()
        self._delta         =   datetime.now() - self._lastupdate
        
        
        self.red            =   [ False ] * 24
        self.green          =   [ False ] * 24
        self._lastred       =   [ False ] * 24
        self._lastgreen     =   [ False ] * 24
        
        for i in range(self._max, 0):
            self.set(i)
        
        # Run initial update
        self.update()
        
    def _color(self, character, color):
        try:
            from termcolor import colored
            return colored(character, color)
        except:
            return character

    def set(self, value):
        try:
            value = int(value)
        except ValueError:
            print "Unexpected value: " + value + ". Ignoring."

        self._lastvalue     =   self.value
        self._delta         =   datetime.now() - self._lastupdate
        self._lastupdate    =   datetime.now()
        self.value          =   value
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
                c    =   self._color(char, "yellow")
            elif self.red[i]:
                c    =   self._color(char, "red")
            elif self.green[i]:
                c    =   self._color(char, "green")
            else:
                c    =   " "
            
            bar+=c
        
        bar += "]"
        return  bar
        
    def format(self):
        def clear():
            self._lastred       =   self.red[:]
            self._lastgreen     =   self.green[:]
            
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
                else:
                    self.green[i]   =   False
                    self.red[i]     =   True
        
        def rainbow():
            percent = float(self.value) * 100 / self._max;
            
            for i in range(0, min(24, int(24*percent/100))):
                if i > 12:
                    self.green[i]   =   True
                elif i > 4:
                    self.green[i]   =   True
                    self.red[i]     =   True
                else:
                    self.green[i]   =   False
                    self.red[i]     =   True
        
        def red():
            percent = float(self.value) * 100 / self._max;
            
            for i in range(0, min(24, int(24*percent/100))):
                self.red[i]         =   True
                
        def green():
            percent = float(self.value) * 100 / self._max;
            
            for i in range(0, min(24, int(24*percent/100))):
                self.green[i]       =   True
                
        def yellow():
            percent = float(self.value) * 100 / self._max;
            
            for i in range(0, min(24, int(24*percent/100))):
                self.red[i]         =   True
                self.green[i]       =   True
        
        def delta():
            green()
            
            percent         =   float(self.value) * 100 / self._max;
            changepermilli  =   float(self.value-self._lastvalue)/(self._delta.total_seconds()*1000)
            projectedchange =   changepermilli * self._showdelta
            percentchange   =   projectedchange / self._max
            
            if percentchange > 0:
                for i in range(min(24, int(24*percent/100)), min(24, int(24*(percent+percentchange)/100))):
                    self.red[i]     =   True
                    self.green[i]   =   True
            elif percentchange < 0:
                for i in range(max(0, (int(24*(percent+percentchange)/100)-1)), min(24, int(24*percent/100))):
                    self.red[i]     =   True
                    self.green[i]   =   False
            
        clear()
        
        if self.value < 0 or self._max < 0:
            self._arduino.bargraphWrite(self.device, self.red, self.green)
            return
        
        f = locals().get(self._type)
        if not f:
            debug("Unknown type: " + self._type)
        
        f()
        
        
    def write(self):
        if cmp(self.red, self._lastred) == 0 and cmp(self.green, self._lastgreen) == 0:
            pass
        else:
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
    import sys
    
    a = arduino()
    
    bar0 = bargraph(a, "Test", "test", 0)
    bar1 = bargraph(a, "Test", "test", 1)
    bar2 = bargraph(a, "Test", "test", 2)
    bar3 = bargraph(a, "Test", "test", 3)
    bar4 = bargraph(a, "Test", "test", 4)
    
    bar0.update()
    bar1.update()
    bar2.update()
    bar3.update()
    bar4.update()
    
    bar0.printout()
    
    import time
    
    for i in range(0, 101):
        bar0.set(i)
        bar1.set(i)
        bar2.set(i)
        bar3.set(i)
        bar4.set(i)
        
        print bar0.toString()
        time.sleep(.25)
        
    for i in range(101, -1, -1):
        bar0.set(i)
        bar1.set(i)
        bar2.set(i)
        bar3.set(i)
        bar4.set(i)
        
        print bar0.toString()
        time.sleep(.25)
        

if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)
