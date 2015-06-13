#!/usr/bin/python

import sys
import logging
from datetime import datetime
from tools import KAPCOMLog

# Logging
_log = KAPCOMLog("Bargraph", logging.WARN)
log = _log.log


class Bargraph(object):
    formats = [
        "default",
        "red",
        "yellow",
        "green",
        "rainbow",
        "delta"
    ]

    def __init__(self, name, api, options=None):
        """Initialize pin with parameters"""
        # Set core attributes
        self.device = None
        self.arduino = None

        self.name = name
        self.api = api
        
        # Pre-set extra attributes
        self.type = "delta"
        self.max = 100
        self.showdelta = 60*1000
        
        # Override defaults with passed values
        if options:
            for key in options:
                setattr(self, key, options[key])
        
        # Set ephemeral values
        self.value = 0
        self._lastvalue = 0
        
        self._lastupdate = datetime.now()
        self._delta = datetime.now() - self._lastupdate
        
        self.red = [False] * 24
        self.green = [False] * 24
        self._lastred = [False] * 24
        self._lastgreen = [False] * 24
        
        for i in range(self.max, 0):
            self.set(i)
        
        # Run initial update
        self.update()

    def attach(self, arduino, device):
        self.arduino = arduino
        self.device = device

    def detatch(self):
        self.arduino = None
        self.device = None

    def is_attached(self):
        if self.arduino is not None and self.device is not None:
            return True
        else:
            return False

    def set(self, value, new_max=None):
        log.debug("Setting bargraph " + self.name + " " + str(value) + "/" + str(new_max))

        if new_max is not None:
            self.max = new_max

        try:
            value = int(value)
        except ValueError:
            print "Unexpected value: " + value + ". Ignoring."

        self._lastvalue = self.value
        self._delta = datetime.now() - self._lastupdate
        self._lastupdate = datetime.now()
        self.value = value
        self.update()

    def update(self):
        self.format()
        self.write()
        
    def printout(self):
        print "Bargraph " + self.name + " (Type = " + self.type + ")"
        print str(self)
        
    def __str__(self):
        bar = "["
        
        for i in range(0, 24):
            if self.red[i] and self.green[i]:
                c = "Y"
            elif self.red[i]:
                c = "R"
            elif self.green[i]:
                c = "G"
            else:
                c = " "
            
            bar += c
        
        bar += "]"
        return bar
        
    def format(self):
        def clear():
            self._lastred = self.red[:]
            self._lastgreen = self.green[:]
            
            for i in range(0, 24):
                self.red[i] = False
                self.green[i] = False
        
        def default():
            percent = float(self.value) * 100 / self.max
            
            for i in range(0, min(24, int(24*percent/100))):
                if percent > 50:
                    self.green[i] = True
                elif percent > 20:
                    self.green[i] = True
                    self.red[i] = True
                else:
                    self.green[i] = False
                    self.red[i] = True
        
        def rainbow():
            percent = float(self.value) * 100 / self.max
            
            for i in range(0, min(24, int(24*percent/100))):
                if i > 12:
                    self.green[i] = True
                elif i > 4:
                    self.green[i] = True
                    self.red[i] = True
                else:
                    self.green[i] = False
                    self.red[i] = True
        
        def red():
            percent = float(self.value) * 100 / self.max
            
            for i in range(0, min(24, int(24*percent/100))):
                self.red[i] = True
                
        def green():
            percent = float(self.value) * 100 / self.max
            
            for i in range(0, min(24, int(24*percent/100))):
                self.green[i] = True
                
        def yellow():
            percent = float(self.value) * 100 / self.max
            
            for i in range(0, min(24, int(24*percent/100))):
                self.red[i] = True
                self.green[i] = True
        
        def delta():
            green()
            percent = float(self.value) * 100 / self.max
            changepermilli = float(self.value-self._lastvalue)/(self._delta.total_seconds()*1000)
            projectedchange = changepermilli * self.showdelta
            percentchange = projectedchange / self.max
            
            if percentchange > 0:
                for i in range(min(24, int(24*percent/100)), min(24, int(24*(percent+percentchange)/100))):
                    self.red[i] = True
                    self.green[i] = True
            elif percentchange < 0:
                for i in range(max(0, (int(24*(percent+percentchange)/100)-1)), min(24, int(24*percent/100))):
                    self.red[i] = True
                    self.green[i] = False
            
        clear()
        
        if self.value < 0 or self.max <= 0:
            self.arduino.bargraph_write(self.device, self.red, self.green)
            return
        
        f = locals().get(self.type)
        if not f:
            log.error("Unknown type: " + self.type)
            return

        try:
            f()
        except ZeroDivisionError:
            log.error("Tried to divide by 0, check the math")

    def write(self):
        if cmp(self.red, self._lastred) == 0 and cmp(self.green, self._lastgreen) == 0:
            log.debug("No change in display, skipping update")
        else:
            self.arduino.bargraph_write(self.device, self.red, self.green)

    def get_data(self):
        if self.is_attached():
            data = {
                "Name": self.name,
                "API": self.api,
                "Type": "Bargraph",
                "Format": self.type,
                "Value": self.value,
                "Arduino": self.arduino.name,
                "Device": self.device,
                "Max": self.max
            }
        else:
            data = {
                "Name": self.name,
                "API": self.api,
                "Type": "Bargraph",
                "Format": self.type,
                "Value": self.value,
                "Arduino": "None",
                "Device": "None",
                "Max": self.max
            }

        return data


# #####################################
# ########## Testing Methods ##########
# #####################################


def main():
    from arduino import Arduino
    from tools import breakpoint
    a = Arduino("Test")
    
    bar = Bargraph(a, "Test", "test")
    
    bar.update()
    
    bar.printout()
    
    import time
    
    for i in range(0, 101):
        bar.set(i)
        print str(bar)
        time.sleep(.25)
        
    for i in range(101, -1, -1):
        bar.set(i)
        
        print str(bar)
        time.sleep(.25)

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
