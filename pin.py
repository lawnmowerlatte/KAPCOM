#!/usr/bin/python

from datetime import datetime
from arduino import arduino

class pin(object):
    """Base class for handling Arduino based I/O"""
    
    # Class Members
    # name
    # api
    # pin
    # value
    # __arduino
    # __format
    # __invert
    # __cooldown
    # __lastupdate
    # __lastvalue

    def __init__(self, arduino, name, api, pin, format="value", cooldown=500, invert=False):
        """Initialize pin with parameters"""
        self.name           =   name
        self.api            =   api
        self.pin            =   pin
        self.__format       =   format
        self.__cooldown     =   cooldown
        self.__invert       =   invert
        self.__arduino      =   arduino
        
        self.init()
        
        self.value          =   0
        self.__lastvalue    =   0
        self.__lastupdate   =   datetime.now()
        self.update()


    def init(self):
        print "Unknown mode for base class."
        
        
    def update(self):
        # Check if cooldown has expired
        delta = self.__lastupdate - datetime.now()
        if (delta.total_seconds()*1000) > self.__cooldown:
            return
        
        # Update counter
        self.__lastupdate =   datetime.now()
        
        # Perform action described in individual class
        self.act()
        
    def act(self):
        print "No action defined for base class."

    def get(self):
        self.update()
        return self.value
    
    def set(self, value):
    	if value == "1" or value == "True" or value == True:
            value = 1
    	if value == "0" or value == "False" or value == False:
            value = 0
        
        self.value = value
        self.update()
    
    def changed(self):
    	changed = (self.__lastvalue != self.value);
    	self.__lastvalue = self.value;
    	return changed
    
    def printout(self):
        print  "{0} ({1})={2}".format(self.name, self.api, self.value)
        
    def toString(self):
        # Define lambdas for selecting value based on format
        value       = lambda x: str(x)
        toggle      = lambda x: (None, "")[x]
        truefalse   = lambda x: ("True", "False")[x]
        true        = lambda x: ("True", "")[x]
        false       = lambda x: ("", "False")[x]
        zero        = lambda x: ("0", "")[x]
        one         = lambda x: ("1", "")[x]
        floatpoint  = lambda x: str(x/self.max)
        percent     = lambda x: str(x/self.max*100)
        
        # Define function for pressing a key
        def key(x):
            """Press a key"""
            keyCommand = "osascript -e 'tell application \"Kerbal Space Program\" to keystroke \""+self.key+"\"'"
            os.system(keyCommand)
        
        # Try to run the lambda/function specified by __format
        try:
            func = getattr(modulename, self.__format)
        except AttributeError:
            print 'Format not found "%s" (%s)' % (self.__format, arg)
        else:
            self.__format(self.value)
          
class analogIn(pin):
    def __init__(self, arduino, name, api, pin, format="value", cooldown=500, invert=False):
        super(analogIn, self).__init__(arduino, name, api, pin, format, cooldown, invert)
    
    def init(self):
        pass
    
    def act(self):
       self.read()
    
    def read(self):
        self.value = self.__arduino.analogRead(self.pin)
    
    
class analogOut(pin):
    def __init__(self, arduino, name, api, pin, format="value", cooldown=500, invert=False):
        super(analogOut, self).__init__(arduino, name, api, pin, format, cooldown, invert)
    
    def init(self):
        self.__arduino.pinMode(self.pin, "OUTPUT")
        
    def act(self):
        self.write()
        
    def write(self):
        self.__arduino.analogWrite(self.pin, self.value)
        
    
class digitalIn(pin):
    def __init__(self, arduino, name, api, pin, format="value", cooldown=500, invert=False):
        super(digitalIn, self).__init__(arduino, name, api, pin, format, cooldown, invert)
    
    def init(self, pullup=True):
        if pullup:
            self.__arduino.pinMode(self.pin, "INPUT_PULLUP")
        else:
            self.__arduino.pinMode(self.pin, "INPUT")
    
    def act(self):
        self.read()
       
    def read(self):
        self.value = self.__arduino.digitalRead(self.pin)
    
    
class digitalOut(pin):
    def __init__(self, arduino, name, api, pin, format="value", cooldown=500, invert=False):
        super(digitalOut, self).__init__(arduino, name, api, pin, format, cooldown, invert)
    
    def init(self):
        self.__arduino.pinMode(self.pin, "OUTPUT")
        
    def act(self):
        self.write()
        
    def write(self):
        self.__arduino.digitalWrite(self.pin, self.value)
    
    

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
    #p = pin(a, "Test", "token", 0x0D, "truefalse")
    #t = analogIn(a, "Throttle", "throttle", 0xA8, "value")
    #l = digitalOut(a, "LED", "led", 0x0D, "value")
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