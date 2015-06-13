import platform
import logging
import serial
from tools import KAPCOMLog

if platform.system() == 'Windows':
    import _winreg as winreg
    import itertools
elif platform.system() == 'Darwin':
    from serial.tools import list_ports
else:
    import glob

# Logging
_log = KAPCOMLog("Arduino", logging.INFO)
log = _log.log


class Arduino(object):
    def __init__(self, name, uuid=None, port=None, baud=115200, timeout=2, s=None, silent=True):
        """Initializes serial communication with Arduino"""

        self.name = name
        self.connected = False
        self.version = "KAPCOM v0.1"
        self.uuid = uuid
        self.silent = silent
        
        if s is None:
            if not port:
                # No port specified, search for a port
                self.s = self._find_port(baud, timeout)
            else:
                # Try to connect to the specified port
                try:
                    self.s = serial.Serial(port, baud, timeout=timeout)
                except (serial.SerialException, OSError):
                    log.error("Specified port is not found.")
                    raise EnvironmentError("Specified port is not found.")

                # Check if the connected device is compatible
                v = self.get_version(s)

                # Retry once in case we missed it
                if v == "":
                    v = self.get_version(s)

                # If not correct, continue search
                if v != self.version:
                    log.error('Bad version "{0}". This is not a KAPCOM/Arduino!'.format(v))
                    raise EnvironmentError('Bad version "{0}". This is not a KAPCOM/Arduino!'.format(v))

                # Check UUID if set
                if self.s is not None and self.uuid is not None:
                    u = self.get_uuid(s)
                    log.debug('Found UUID: ' + u)

                    if self.uuid != u:
                        log.error("Specified port does not match the UUID.")
                        raise EnvironmentError("Specified port does not match the UUID.")

            if not self.s:
                log.warn("Using interactive mode.")
            else:
                self.s.flush()
        else:
            self.s = s

        if self.s is None:
            self.connected = False
        else:
            self.connected = True

    def _find_port(self, baud, timeout):
        """Find the first port that is connected to an Arduino with a compatible sketch installed."""
    
        # Get a list of serial ports depending on the platform
        if platform.system() == 'Windows':
            ports = self._enumerate_serial_ports()
        elif platform.system() == 'Darwin':
            ports = [i[0] for i in list_ports.comports() if 'Bluetooth' not in i[0]]
        else:
            ports = glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        
        # Iterate over ports to test
        for p in ports:
            log.debug('Found {0}, testing...'.format(p))
            
            # If connection fails, continue search
            try:
                s = serial.Serial(p, baud, timeout=timeout)
            except (serial.SerialException, OSError) as e:
                log.warn(str(e))
                continue
                
            # Check if the connected device is compatible
            v = self.get_version(s)
            
            # Retry once in case we missed it
            if v == "":
                v = self.get_version(s)
            
            # If not correct, continue search
            if v != self.version:
                log.debug('Bad version "{0}". This is not a KAPCOM/Arduino!'.format(v))
                s.close()
                continue

            # Check UUID if set
            if self.uuid is not None:
                u = self.get_uuid(s)
                log.debug('Found UUID: ' + u)

                if self.uuid != u:
                    log.debug('UUID did not match')
                    s.close()
                    continue

            # Version and UUID matches
            log.info('Using port {0}.'.format(p))
            if s:
                return s
        
        # Search failed
        return None

    @staticmethod
    def _enumerate_serial_ports():
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

    @staticmethod
    def _build_command(command, device=None, data=None, remap=True):
        """Build a command string that can be sent to the Arduino"""
        
        if remap:
            if device is not None:
                # Remap pin to avoid ASCII control characters
                device += 32
                
                # Concatenate the byte value of the pin we are sent
                command += chr(device)
                
                if data is not None:
                    # Concatenate whatever data is sent
                    command += str(data)
        else:
            if device is not None:
                # Concatenate the byte value of the pin we are sent
                command += str(device)
                if data is not None:
                    # Concatenate whatever data is sent
                    command += str(data)
                    
        return command

    def _write(self, string, s=None):
        """Write the string to serial"""

        if not s and not self.s:
            if not self.silent:
                print("<< " + string)
            return
        
        return self._readwrite(string, s)

    def _read(self, string, s=None):
        """Write the string to serial and return the response"""
        
        if not s and not self.s:
            if not self.silent:
                print("<< " + string)
                return raw_input(">> ")
            return 1
        
        self._readwrite(string, s)

    def _readwrite(self, string, s=None):
        log.debug(string)

        if not s:
            s = self.s

        try:
            s.write(string + "\n")
            s.flush()
        except serial.SerialException:
            log.critical("Serial error while writing, check the connection")
            return ""

        try:
            return s.readline().replace("\r\n", "")
        except serial.SerialException:
            log.critical("Serial error while reading, check the connection")
            return ""

    def _close(self):
        """Closes the serial connection"""
        log.info("Closing connection to Arduino")

        if self.s.isOpen():
            self.s.flush()
            self.s.close()

    def get_version(self, s=None):
        """Return the version of the connected Arduino"""
        
        return self._read(self._build_command("v"), s)

    def get_uuid(self, s=None):
        """Return the UUID of the connected Arduino"""

        return self._read(self._build_command("u"), s)

    def digital_write(self, pin, value):
        """Sends digitalWrite command to digital pin on Arduino"""
        
        if value == 0 or str(value).upper() == "LOW" or str(value).upper() == "OFF":
            value = 0
        elif value == 1 or str(value).upper() == "HIGH" or str(value).upper() == "ON":
            value = 1
        else:
            log.error("Unexpected value in digitalWrite: " + str(value))
            return
            
        self._write(self._build_command("d", pin, str(value)))

    def analog_write(self, pin, value):
        """Sends analogReadWrite command to pin on Arduino"""
        
        if value > 255:
            value = 255
        elif value < 0:
            value = 0
        
        self._write(self._build_command("a", pin, value))

    def analog_read(self, pin):
        """Returns the value of a specified pin"""
        
        # Check that pin is in expected range
        if pin < 0xA0:
            log.error("Pin too low for analogRead")
            return
        
        # When building command, don't use A
        return self._read(self._build_command("A", pin - 0xA0))

    def digital_read(self, pin):
        """Returns the value of a specified pin"""
        
        return self._read(self._build_command("D", pin))
        
    def subscribe(self, pins):
        """Subscribe to a set of pins"""
        string = ""
        for pin in pins:
            string += chr(pin)
        
        self._write(self._build_command("s", string))
        
    def poll_subscriptions(self):
        """Return values for subscriptions as a list"""
        array = []
        raw = self._read(self._build_command("S"))
        for c in raw:
            array.append(ord(c))
            
        return array
        
    def display_write(self, device, data):
        """Sends command to 7-segment display"""
        self._write(self._build_command("7", device, data, False))

    def bargraph_write(self, device, red, green):
        """Sends command to 24 LED bargraph"""
        
        if len(red) != 24 or len(green) != 24:
            print("Unexpected data length while writing bargraph")
            return
        
        # Pre-populate data bytes with 01000000
        r = [128, 128, 128, 128]
        g = [128, 128, 128, 128]
        
        # Iterate over bytes
        for i in range(0, 4):
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
        for i in range(0, 4):
            data += chr(r[i])
        for i in range(0, 4):
            data += chr(g[i])
        
        self._write(self._build_command("b", device, data, False))

    def pin_mode(self, pin, value):
        """Sets I/O mode of pin"""
        
        if value == "OUTPUT":
            data = "0"
        elif value == "INPUT":
            data = "1"
        elif value == "INPUT_PULLUP":
            data = "2"
        else:
            data = "{0}".format(value)
        
        self._write(self._build_command("m", pin, data))