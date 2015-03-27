#!/usr/bin/python

from abc import ABCMeta, abstractmethod
from datetime import datetime
from arduino import arduino

class pin(object):
    __metaclass__ = ABCMeta
    
    ## Core Class Members
    # name
    # api
    # pin
    # value
    # _arduino
    # _format
    # _invert
    # _cooldown
    # _lastupdate
    # _lastvalue
    
    ## Optional Class Members
    # _max
    
    def __init__(self, arduino, name, api, pin, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self._arduino       =   arduino
        self.name           =   name
        self.api            =   api
        self.pin            =   pin
        
        # Pre-set extra attributes
        self._cooldown       =   500
        self._invert         =   False
        self._format         =   "value"
        self._max            =   1024
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Initialize the hardware
        self.init()
        
        # Set ephemeral values
        self.value          =   0
        self._lastvalue     =   0
        self._lastupdate    =   datetime.now()
        
        # Run initial update
        self.update()
        
    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def act(self, value=None):
        pass
        
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
        
    def update(self, value=None):
        # Check if cooldown has expired
        delta = self._lastupdate - datetime.now()
        if (delta.total_seconds()*1000) > self._cooldown:
            return
        
        # Update counter
        self._lastupdate =   datetime.now()
        
        # Perform action described in individual class
        self.act(value)
    
    def changed(self):
    	changed = (self._lastvalue != self.value);
    	self._lastvalue = self.value;
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
            self._format(self.value)
        except AttributeError:
            print 'Format not found "%s"' % (self._format)
            
    
class __input(pin):
    __metaclass__ = ABCMeta
    
    def init(self):
        self._arduino.pinMode(self.pin, "INPUT_PULLUP")
    
    def act(self, value=None):
        return self.read()

class __output(pin):
    __metaclass__ = ABCMeta
    
    def init(self):
        self._arduino.pinMode(self.pin, "OUTPUT")
        pass
    
    def act(self, value):
        self.write(value)
        
class __analog():
    __metaclass__ = ABCMeta
    
    def setMax(self, max):
        self._max = max
        
    def getFloat(self):
        self.update()
        return (float(self.value)/self._max)
    
    def read(self):
        self.value = int(self._arduino.analogRead(self.pin))
        return self.value
        
    def write(self, value):
        if value:
            self.value = int(value)
            self._arduino.analogWrite(self.pin, self.value)

class __digital():
    __metaclass__ = ABCMeta
    
    def read(self):
        self.value = int(self._arduino.digitalRead(self.pin))
        return self.value
        
    def write(self, value):
        if value:
            self.value = int(value)
            self._arduino.digitalWrite(self.pin, self.value)
        
class analogIn(__analog, __input):
    pass
    
class analogOut(__analog, __output):
    pass
    
class digitalIn(__digital, __input):
    pass
    
class digitalOut(__digital, __output):
    pass

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
    #a = arduino("/dev/cu.usbmodem1411")
    aI = analogIn(a, "Throttle", "throttle", 0xA8)
    aO = analogOut(a, "Dimmer", "dimmer", 0x08)
    dI = digitalIn(a, "SAS", "sas", 0x0A)
    dO = digitalOut(a, "SAS Status", "sas_status", 0x0B)
    
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