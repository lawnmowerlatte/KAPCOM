#!/usr/bin/python

from arduino import arduino
from termcolor import colored

class display(object):
    def __init__(self, arduino, name, api, device, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self._arduino       =   arduino
        self.name           =   name
        self.api            =   api
        self.device         =   device
        
        # Pre-set extra attributes
        self._type          =   "default"
        self._length        =   8
        self._offset        =   0
        self._decimals      =   3
        self._pad           =   " "
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, "_" + key, options[key])
        
        # Set ephemeral values
        self.value        =   self._pad * self._length
        
        # Run initial update
        #self.update()

    def set(self, value):
        self.value = value
        self.format()
        self.update()
        
    def update(self):
        self.write()
        
    def printout(self):
        print "Display " + self.name
        print self.toString()
        
    def toString(self):
        return "[" + colored(self.value, "cyan") + "]"
        
    def format(self):
        # Take the value passed and format it for the 8 digit seven-segment display
         
        # Counter for exponents when using scientific notation
        E           =   ""
        exponent    =   0
     
        # Break the value into integer and decimal portions
        value       =   '{0:f}'.format(self.value)
        integer     =   value[:value.index('.')]
        decimal     =   value[value.index('.')+1:]
        
        if len(integer) > self._length:
            significant = len(integer)

            # print "Value:       " + str(self.value)
            # print "Exponent:    " + str(exponent)
            # print "New Value:   " + value
            # print "Significant: " + str(significant)
            # print "Calculating..."
            
            while significant + len(str(exponent)) + 1 > self._length:
                exponent+=3
                significant = len(integer) - exponent
                 
            # print "Exponent:    " + str(exponent)
            # print "Significant: " + str(significant)
            
            formatted = value[:significant] + "E" + str(exponent)
            
            # print "Formatted:   " + formatted
            decimals = self._length - len(formatted)
            # print "Decimals:    " + str(decimals)
            if decimals > 0:
                 formatted = value[:significant] + "." + value[significant:significant+decimals] + "E" + str(exponent)
              
            # print "Reformatted: " + formatted
        
        elif len(integer) < self._length:
            # Fewer integers than can be displayed
            # Attempt to fill with decimals
          
            # Truncate the decimals to fit on the display
            decimal = decimal[:self._length-len(integer)]
          
            # Truncate the decimals according to maximum decimal length
            if (len(decimal) > self._decimals): 
                decimal = decimal[:self._decimals]
              
            # Create formatted string
            formatted = integer + "." + decimal
          
        else:
            # Integers fill display
            formatted = integer + ".";
         
        # Pad string if it's too short
        if len(formatted.replace(".", "")) < self._length:
            for i in range(0, self._length - len(formatted.replace(".", ""))):
                formatted = self._pad + formatted
     
        # Final check for string length
        if len(formatted.replace(".", "")) != self._length:
            # Print a debug message
            print("Something went wrong while formatting: " + str(self.value) + " >> " + formatted)
              
            # Set the display to dashes
            formatted = "-" * self._length;
        
        self.value = formatted

    def write(self):
        self._arduino.displayWrite(self.device, self.value)


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
    d = display(None, "Test", "test", 0)
    
    import time
    
    value = .00000012345678
    
    for i in range(0,20):
        d.value = value
        d.format()
        print d.toString()
        
        value *= 10
    
    # breakpoint()

if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)
