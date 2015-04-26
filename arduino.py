#!/usr/bin/python

import platform
import serial
import time

if platform.system() == 'Windows':
    import _winreg as winreg
    import itertools
elif platform.system() == 'Darwin':
    from serial.tools import list_ports
else:
    import glob

debugger = 2
def debug(message, level=debugger, newline=True):
    if level <= debugger:
        if newline:
            print(message) 
        else:
            sys.stdout.write(message)

class arduino(object):
    def __init__(self, port=None, baud=115200, timeout=2, s=None, silent=True):
        """Initializes serial communication with Arduino"""
        
        self.connected = False
        self.version = "KAPCOM v0.1"
        self.silent = silent
        
        if not s:
            if not port:
                # No port specified, search for a port
                self.s = self.find_port(baud, timeout)
            else:
                # Try to connect to the specified port
                try:
                    self.s = serial.Serial(port, baud, timeout=timeout)
                except (serial.serialutil.SerialException, OSError) as e:
                    debug("Specified port is not found.", 4)
                    self.s = None
                
            if not self.s:
                debug("Using interactive mode.", 2)
            else:
                self.s.flush()
        else:
            self.s = s
                
                
    def find_port(self, baud, timeout):
        """Find the first port that is connected to an arduino with a compatible sketch installed."""
    
        # Get a list of serial ports depending on the platform
        if platform.system() == 'Windows':
            ports = self.enumerate_serial_ports()
        elif platform.system() == 'Darwin':
            ports = [i[0] for i in list_ports.comports()]
        else:
            ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        
        # Iterate over ports to test
        for p in ports:
            debug('Found {0}, testing...'.format(p), 4)
            
            # If connection fails, continue search
            try:
                s = serial.Serial(p, baud, timeout=timeout)
            except (serial.serialutil.SerialException, OSError) as e:
                debug(str(e), 4)
                continue
                
            # Check if the connected device is compatible
            v = self.getVersion(s)
            
            # Retry once in case we missed it
            if v == "":
                v = self.getVersion(s)
            
            # If not correct, continue search
            if v != self.version:
                debug('Bad version "{0}". This is not a KAPCOM/Arduino!'.format(v), 4)
                s.close()
                continue
                
            # Version matches    
            debug('Using port {0}.'.format(p), 3)
            if s:
                return s
        
        # Search failed
        return None
        
    def enumerate_serial_ports(self):
        """Uses the registry to return serial ports"""
    
        path = 'HARDWARE\\DEVICEMAP\\SERIALCOMM'
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        except WindowsError:
            raise Exception
  
        for i in itertools.count():
            try:
                val = winreg.EnumValue(key, i)
                yield (str(val[1]))  # , str(val[0]))
            except EnvironmentError:
                break


    def command(self, command, device=None, data=None, remap=True):
        """Build a command string that can be sent to the Arduino"""
        
        if remap:
            if device is not None:
                # Remap pin to avoid ASCII control characters
                device+=32
                
                # Concatenate the byte value of the pin we are sent
                command=command+chr(device)
                
                if data is not None:
                    # Concatenate whatever data is sent
                    command=command+str(data)
        else:
            if device is not None:
                # Concatenate the byte value of the pin we are sent
                command=command+str(device)
                if data is not None:
                    # Concatenate whatever data is sent
                    command=command+str(data)
                    
        return command


    def write(self, string, serial=None):
        """Write the string to serial"""

        if not serial and not self.s:
            if not self.silent:
                print("<< " + string)
            return
        
        debug(string, 5)
        
        if not serial:
            serial = self.s
        
        try:
            serial.write(string + "\n")
            serial.flush()
        except:
            pass
            
        serial.readline()
        
    
    def read(self, string, serial=None):
        """Write the string to serial and return the response"""
        
        if not serial and not self.s:
            if not self.silent:
                print("<< " + string)
                return raw_input(">> ")
            return 1
        
        debug(string, 5)
        
        if not serial:
            serial = self.s
        
        try:
            serial.write(string + "\n")
            serial.flush()
        except:
            pass
            
        return serial.readline().replace("\r\n", "")
    
    
    def getVersion(self, serial=None):
        """Return the version of the connected Arduino"""
        
        return self.read(self.command("v"), serial)


    def digitalWrite(self, pin, value):
        """Sends digitalWrite command to digital pin on Arduino"""
        
        if value == 0 or str(value).upper() == "LOW" or str(value).upper() == "OFF":
            value=0
        elif value == 1 or str(value).upper() == "HIGH" or str(value).upper() == "ON":
            value=1
        else:
            debug("Unexpected value in digitalWrite: " + str(value))
            return
            
        self.write(self.command("d", pin, str(value)))


    def analogWrite(self, pin, value):
        """Sends analogReadWrite command to pin on Arduino"""
        
        if value > 255:
            value = 255
        elif value < 0:
            value = 0
        
        self.write(self.command("a", pin, value))


    def analogRead(self, pin):
        """Returns the value of a specified pin"""
        
        # Check that pin is in expected range
        if pin < 0xA0:
            debug("Pin too low for analogRead")
            return
        
        # When building command, don't use A
        return self.read(self.command("A", pin - 0xA0))


    def digitalRead(self, pin):
        """Returns the value of a specified pin"""
        
        return self.read(self.command("D", pin))
        
    def subscribe(self, pins):
        """Subscribe to a set of pins"""
        string =""
        for pin in pins:
            string += chr(pin)
        
        self.write(self.command("s", string))
        
    def getSubscriptions(self):
        """Return values for subscriptions as a list"""
        array   =   []
        raw     =   self.read(self.command("S"))
        for c in raw:
            array.append(ord(c))
            
        return array
        
    def displayWrite(self, device, data):
        """Sends command to 7-segment display"""
        self.write(self.command("7", device, data, False))
        
        
    def bargraphWrite(self, device, red, green):
        """Sends command to 24 LED bargraph"""
        
        if len(red) != 24 or len(green) != 24:
            print("Unexpected data length while writing bargraph")
            return
        
        # Pre-populate data bytes with 01000000
        r = [ 128, 128, 128, 128 ]
        g = [ 128, 128, 128, 128 ]
        
        # Iterate over bytes
        for i in range(0,4):
            # Iterate over bits
            for j in range(1, 7):
                # If the passed value is True
                if red[i*6+j-1] is True:
                    # Write a 1 into the bit
                    r[i] += 1 << 6-j
                # If the passed value is True
                if green[i*6+j-1] is True:
                    # Write a 1 into the bit
                    g[i] += 1 << 6-j
                
        data = ""
        # Assemble bytes
        for i in range(0,4):
            data += chr(r[i])
        for i in range(0,4):
            data += chr(g[i])
        
        self.write(self.command("b", device, data, False))
        

    def pinMode(self, pin, value):
        """Sets I/O mode of pin"""
        
        if value == "OUTPUT":
            data = "0"
        elif value == "INPUT":
            data = "1"
        elif value == "INPUT_PULLUP":
            data = "2"
        else:
            data="{0}".format(value)
        
        self.write(self.command("m", pin, data))


    def close(self):
        """Closes the serial connection"""
        if self.s.isOpen():
            self.s.flush()
            self.s.close()
