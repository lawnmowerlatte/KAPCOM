#!/usr/bin/python

import os
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
        self._cooldown      =   500
        self._invert        =   False
        self._format        =   "value"
        self._max           =   1024
        self._deadzone      =   0
        self._initial       =   0
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Initialize the hardware
        self.init()
        
        # Set ephemeral values
        self.value          =   self._initial
        self._lastvalue     =   self.value
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
        
    def push(self, value):
        """Attempts to push the selected value and update"""
    	if value == "1" or value == "True" or value == True:
            value = 1
    	if value == "0" or value == "False" or value == False:
            value = 0
        
        return self.update(self, value)
        
    def set(self, value):
        """Set the value and update"""
    	if value == "1" or value == "True" or value == True:
            value = 1
    	if value == "0" or value == "False" or value == False:
            value = 0
        
        self.update(value)
        
    def update(self, value=None):
        """Check cooldown timer and act"""
        # Check if cooldown has expired
        delta = self._lastupdate - datetime.now()
        if (delta.total_seconds()*1000) > self._cooldown:
            print "cooldown not reached"
            return
        # Update counter
        self._lastupdate =   datetime.now()
        # Perform action described in individual class
        self.act(value)
    
    def changed(self):
        """Check if value has changed since last check"""
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
        floatpoint  = lambda x: str(float(x)/self._max)
        percent     = lambda x: str(float(x)/self._max*100)
        
        # Define function for pressing a key
        def key(x):
            """Press a key"""
            keyCommand = "osascript -e 'tell application \"Kerbal Space Program\" to keystroke \""+self._key+"\"'"
            if x is 1:
                print keyCommand
                #os.system(keyCommand)
        
        # Try to run the lambda/function specified by _format
        f = locals().get(self._format)
        try:
            return f(self.value)
        except AttributeError:
            print 'Format not found "%s"' % (self._format)
        
        return ""
    
class __input(pin):
    __metaclass__ = ABCMeta
    
    def init(self):
        self._arduino.pinMode(self.pin, "INPUT_PULLUP")
    
    def act(self, value=None):
        """If no value is passed, read"""
        if value is None:
            return self.read()

class __output(pin):
    __metaclass__ = ABCMeta
    
    def init(self):
        """Set the hardware and local value"""
        self._arduino.pinMode(self.pin, "OUTPUT")
        self._cooldown = 0
        pass
    
    def act(self, value):
        """Write the value"""
        self.write(value)
        
class __analog():
    __metaclass__ = ABCMeta
    
    def setMax(self, max):
        """Set the maximum value"""
        self._max = max
        
    def getFloat(self):
        """Update the hardware and return latest value"""
        self.update()
        return (float(self.value)/self._max)
    
    def changed(self):
        """Check if value has changed significantly since last check"""
    	changed = float(self._lastvalue - self.value)/self._max*100;
        
        if abs(changed) > 1:
            self._lastvalue = self.value;
            return True
        else:
            return False
    
    def read(self):
        """Read from hardware"""
        self.value = int(self._arduino.analogRead(self.pin))
        
        if self._invert:
            self.value = self._max - self.value
        
        if self.value < self._max * self._deadzone:
            self.value = 0
        elif self.value > self._max * (1-self._deadzone):
            self.value = self._max
        
        return self.value
        
    def write(self, value):
        """Write to hardware"""
        if value:
            self.value = int(value)
            
            if self._invert:
                self.value = self._max - self.value
            
            self._arduino.analogWrite(self.pin, self.value)

class __digital():
    __metaclass__ = ABCMeta
    
    def read(self):
        """Read from hardware"""
        self.value = int(self._arduino.digitalRead(self.pin))
        
        if self._invert:
            if self.value == 0:
                self.value = 1
            elif self.value == 1:
                self.value = 0
            else:
                print "Unexpected value"
            
        return self.value
        
    def write(self, value):
        """Write to hardware"""
        
        if value is not None:
            self.value = int(value)
            
            if self._invert:
                if self.value == 0:
                    self.value = 1
                elif self.value == 1:
                    self.value = 0
                else:
                    print "Unexpected value"
            
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