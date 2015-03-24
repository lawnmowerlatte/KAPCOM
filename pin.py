#define ANALOG 1
#define DIGITAL 0
#define NULL 0

from datetime import datetime

class Pin:
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

    def __init__(self, arduino, name, api, pin, format, cooldown, invert):
        self.name       =   name
        self.api        =   api
        self.pin        =   pin
        self.__format   =   format
        self.__cooldown =   cooldown
        self.__invert   =   invert
        self.__arduino  =   arduino
        
        self.init()
        
        self.value      =   0
        self.update()

        



    def init(self):
        print "Unknown mode for base class."
        
        
        
        
    def update(self):
        # Check if cooldown has expired
        delta = self.lastupdate - datetime.now()
        if (delta.total_seconds*1000 > self.cooldown):
            return
        
        # Update counter
        self.lastupdate =   datetime.now()
        
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
    	changed = (self.lastvalue != self.value);
    	selflastvalue = self.value;
    	return changed
    
    def printout(self):
        print  "{0} ({1})={2}".format(self.name, self.api, self.value)
        
    def toString(self):
        return self.value
        

class input(Pin):
    def init(self, pullup=True):
        if pullup:
            self.arduino.pinMode(self.pin, "INPUT_PULLUP")
        else:
            self.arduino.pinMode(self.pin, "INPUT")
    
    def act(self):
       self.read()
       
    def toString(self):
        value       = lambda x: String(x)
        toggle      = lambda x: (None, "")[x]
        truefalse   = lambda x: ("True", "False")[x]
        true        = lambda x: ("True", "")[x]
        false       = lambda x: ("", "False")[x]
        zero        = lambda x: ("0", "")[x]
        one         = lambda x: ("1", "")[x]
        key         = lambda x: (self.key, "")[x]
        floatpoint  = lambda x: str(x/self.max)
        percent     = lambda x: str(x/self.max*100)
        
        try:
            func = getattr(modulename, self.__format)
        except AttributeError:
            print 'Format not found "%s" (%s)' % (self.__format, arg)
        else:
            self.__format(self.value)
       
       
class output(Pin):
    def init(self):
        self.arduino.pinMode(self.pin, "OUTPUT")
        
    def act(self):
        self.write()
    
    
class digital(Pin):
    def read(self):
        self.value = self.arduino.digitalRead(self.pin)
        
    def write(self):
        self.arduino.digitalWrite(self.pin, self.value)


class analog(Pin):
    def read(self):
        self.value = self.arduino.analogRead(self.pin)
        
    def write(self):
        self.arduino.analogWrite(self.pin, self.value)
    
    
class analogIn(analog, input):
    pass

class analogOut(analog, output):
    pass
    
class digitalIn(digital, input):
    pass
    
class digitalOut(digital, output):
    pass


