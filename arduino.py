#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# This module interfaces with a connected Arduino via serial connection
# and an API library for communication with Kerbal Space Program. This
# has been initially written to use the Telemachus API library with the
# Telemachus WebSocket API, but is designed to be modular enough that it
# could be replaced in the future without needing to rewrite this library.

debugger = 2

import sys
import socket
import time
import serial
import os
import linecache
import math
import pyksp
import json
import atexit
import platform
import glob

sequence=0
retransmits=0
time_count=0
time_sum=0

def debug(message, level=debugger, newline=True):
    if level <= debugger:
        if newline:
            print(message) 
        else:
            sys.stdout.write(message)

class arduino:
    """Creates an interface between the Arduino serial connection and Telemachus library."""
    
    # Use these for simulation and debugging
    # This overrides the serial port with input from the interactive shell
    interactive = False
    ## This overrides the Telemachus port with static simulated input
    headless = True
    
    buffer = ""
    
    # Specify either a specific port or list of ports to prefer to connect to
    # If neither are set, the script will try to detect your serial port
    
    # port = "/dev/tty.usbmodem1411"
    port = None
    ports = [ "/dev/tty.usbmodem1411", "/dev/tty.usbmodem1421" ]
    #ports  = None
    
    subscriptions = {
        "pause_state",
        "vessel_altitude",
        "vessel_apoapsis",
        "vessel_periapsis",
        "vessel_velocity",
        "vessel_inclination",
        "vessel_asl_height",
        
        "resource_ox_max",
        "resource_ox_current",
        "resource_lf_max",
        "resource_lf_current",
        "resource_mp_max",
        "resource_mp_current",
        "resource_ec_max",
        "resource_ec_current",
        
        "sas_status",
        "rcs_status",
        "action_group_light",
        "action_group_gear",
        "action_group_brake"
    }
    
    def __init__(self, port=None, baud=250000):
        """Takes an API object, serial port and baudrate and creates a new Arduino object."""
        if port is not None:
            self.port = port
        self.baud = baud
        
        if not self.headless:
            self.vessel = pyksp.ActiveVessel()
            for subscription in self.subscriptions:
                self.vessel.subscribe(subscription)
        else:
            debug("Using dummy telemetry", 3)
            
        if not self.interactive:
            if self.port is None:
                if self.ports is None:
                    self.ports = self.listSerial()
                
                self.ports = self.trySerial(self.ports)
                
                if len(self.ports) is 0:
                    debug("No serial ports found.")
                    raw_input("Press [Enter] to retry.\n")
                    main()
                
                if len(self.ports) is 1:
                    self.port = self.ports[0]
                else:
                    for index, port in enumerate(self.ports):
                        debug(str(index) + ": " + port)
                    index = raw_input("Press [#] to connect: ")
                    self.port = self.ports[int(index)]

            try:
                self.serial.close()
            except:
                pass
                
            if not self.openSerial(self.port, self.baud):
                debug("Unable to connect to specified port.")
                raw_input("Press [Enter] to retry.\n")
                main()
            
        else:
            debug("Using shell input", 3)
    
    # Serial manipulation methods
    def openSerial(self, port, baud):
        try:
            self.serial = serial.Serial(
                port,
                baud,
                timeout=.1)
            return True
        except serial.SerialException:
            debug("Port " + port + " in use.")
            raw_input("Press [Enter] to retry.\n")
            return openSerial(port, baud)
        except:
            return False
    
    def listSerial(self):
        sys = platform.system()
        available = []
        
        if sys == "Windows":
            # Scan for available ports.
            
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    available.append(i)
                    s.close()
                except serial.SerialException:
                    pass
        elif sys == "Darwin":
            # Mac
            available = glob.glob('/dev/tty.*') + glob.glob('/dev/cu.*')
        else:
            # Assume Linux or something else
            available = glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*')
        
        return available
    
    def trySerial(self, available):
        for port in available:
            if not self.openSerial(port, self.baud):
                available.remove(port)
        
        return available
        
    
    def readSerial(self, retry=False):
        """Read a line from serial"""
        if self.interactive:
            line = raw_input("> ")
        else:
            line = ""
            
            if retry:
                while not line:
                    line = self.serial.readline()
        
                    if line is "":
                        self.serial.write("{}\n")
                        print "Poking..."
            else:
                try:
                    line = self.serial.readline()
                except serial.SerialException:
                    debug("Lost connection to device.")
                    exit(1)
                
        return line
    
    def writeSerial(self, line):
        """Write a line to serial"""
        if self.interactive:
            print "< " + line
        else:
            try:
                self.serial.write(line + "\n")
            except serial.SerialException:
                debug("Lost connection to device.")
                exit(1)
    
    # Init and Readiness methods
    def init(self):
        debug("Telemetry...", 2, False)
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex(("127.0.0.1", 8085))
            if r == 0:
                self.vessel.start()
                time.sleep(1)
            else:
                self.hold("Unable to connect to telemetry")
                return False
        self.timer(10)
        while not self.ready():
            i = self.tick()
            if i is False:
                self.hold("Timeout while waiting for telemetry.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 2)
        
        debug("Arduino...", 2, False)
        self.timer(5)
        self.writeSerial("RESTART")
        while not self.interactive and "ONLINE" not in self.readSerial(False):
            i = self.tick()
            if i is False:
                self.hold("Timeout while waiting for Arduino.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 2)
        
        debug("Calibration...", 2, False)
        self.timer(10)
        while not self.interactive and "CALIBRATING" not in self.readSerial(False):
            i = self.tick()
            if i is False:
                self.hold("Timeout while calibrating.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 2)
        
        debug("Fly by wire...", 2, False)
        self.timer(5)
        while not self.interactive and "READY" not in self.readSerial(False):
            i = self.tick()
            if i is False:
                self.hold("Timeout while connecting to inputs.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 2)
        
        debug("All stations are go.", 1) 
        return True
    
    def timer(self, i):
        self.i = i
    
    def tick(self):
        if self.i > 0:
            self.i -= 1
            time.sleep(1)
            return True
        else:
            return False
    
    def hold(self, message):
        debug("We have a hold for launch.", 1)
        debug(message, 2)
    
    def ready(self):
        connectionState = False
        
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex(("127.0.0.1", 8085))
            if r == 0:
                connectionState = self.vessel.test_connection()
                debug("Connection state: " + str(connectionState), 5)
        else:
            connectionState = True
        
        return connectionState

    def do(self):
        if not self.headless and self.ready():
            state = self.vessel.get("pause_state")
            debug("Telemachus state: " + str(state), 5)
        else:
            state = 0
        
        if state is 0:
            self.online()
        elif state is 1:
            self.paused()
        elif state is 2:
            self.unpowered()
        elif state is 3:
            self.off()
        elif state is 4:
            self.missing()
        elif state is None:
            self.menu()
        else:
            debug("Unhandled game state: " + str(state), 1)
    
    # Game state methods
    def online(self):
        global sequence
        global retransmits
        global time_count
        global time_sum
        
        sequence+=1
        
        t0 = time.time()
        
        json = self.readOutput()
        self.sendOutput(json)
        
        data = ""
        while data is "":
            data = self.readInput()
            
            if data is "":
                self.sendOutput("{}")
                retransmits+=1

        self.sendInput(data)
        
        t = time.time() - t0
        time_count+=1
        time_sum+=t
        debug("%-2f" % t, 5)

    def unpowered(self):
        print "Antenna is unpowered"
        raw_input("Press [Enter] to retry")
        
    def missing(self):
        print "No antenna found"
        raw_input("Press [Enter] to retry")
        
    def off(self):
        print "Antenna is off"
        raw_input("Press [Enter] to retry")
        
    def paused(self):
        print "Paused"
        currentState = self.vessel.get("pause_state")
        while currentState == 1:
            time.sleep(1)
            currentState = self.vessel.get("pause_state")
        print "Unpaused"

    def menu(self):
        print "Waiting for vessel"
        currentState = self.vessel.get("pause_state")
        while currentState == None:
            time.sleep(1)
            currentState = self.vessel.get("pause_state")
        print "Vessel ready for connection"
        
    # Data processing methods
    def readOutput(self):
        """Read Telemachus telemetry"""
        debug("Read telemetry", 4)
        
        json = self.toJSON()
        return json
    
    def toJSON(self):
        """Return JSON string of the output"""
        debug("Generate JSON", 4)
        
        if self.headless:
            jdata=json.dumps({
                    "vessel_altitude": 8549.71202316096,
                    "vessel_apoapsis": 9478.33655130339,
                    "vessel_periapsis": 4127.25709812508,
                    "vessel_velocity": 158.384706582312,
                    "vessel_inclination": 0.201299374925592,
                
                    "resource_lf_current": -1,
                    "resource_lf_max": -1,
                    "resource_mp_current": 253.60484143293,
                    "resource_mp_max": 275,
                    "resource_ox_current": -1,
                    "resource_ox_max": -1,
                    "resource_ec_current": 49.9994867002824,
                    "resource_ec_max": 50,
        
                    "sas_status": "True",
                    "rcs_status": "False",
                    "action_group_light": "False",
                    "action_group_gear": "False",
                    "action_group_brake": "False"
                })
        else:
            jdata=json.dumps({
                    "vessel_altitude": self.vessel.get("vessel_altitude"),
                    "vessel_apoapsis": self.vessel.get("vessel_apoapsis"),
                    "vessel_periapsis": self.vessel.get("vessel_periapsis"),
                    "vessel_velocity": self.vessel.get("vessel_velocity"),
                    "vessel_inclination": self.vessel.get("vessel_inclination"),
                    
                    "resource_lf_current": self.vessel.get("resource_ox_current"),
                    "resource_lf_max": self.vessel.get("resource_ox_max"),
                    "resource_mp_current": self.vessel.get("resource_mp_current"),
                    "resource_mp_max": self.vessel.get("resource_mp_max"),
                    "resource_ox_current": self.vessel.get("resource_ox_current"),
                    "resource_ox_max": self.vessel.get("resource_ox_max"),
                    "resource_ec_current": self.vessel.get("resource_ec_current"),
                    "resource_ec_max": self.vessel.get("resource_ec_max"),
                    
                    "sas_status": self.vessel.get("sas_status"),
                    "rcs_status": self.vessel.get("rcs_status"),
                    "action_group_light": self.vessel.get("action_group_light"),
                    "action_group_gear": self.vessel.get("action_group_gear"),
                    "action_group_brake": self.vessel.get("action_group_brake")
                })
        
        return jdata
    
    def sendOutput(self, json):
        """Send JSON data to Arduino"""
        debug("Send output", 4)
        
        if json:
            debug(json, 5)
            self.writeSerial(json)
        else:
            debug("< No JSON data to send", 1)
    
    def readInput(self):
        """Poll Arduino for line of input containing JSON data"""
        debug("Read input", 4)
        json = self.readSerial()
        debug(json, 5)
        return json
    
    def fromJSON(self, jdata):
        """Parse JSON input from Arduino"""
        debug("Parse JSON", 4)
        
        try:
            data = json.loads(jdata)
            return data
        except:
            debug("No JSON data found in string: " + str(jdata))
        
    
    def sendInput(self, json):
        """Send Telemachus commands based on input"""
        debug("Parse JSON", 4)
        data = self.fromJSON(json)
        
        if data:
            debug(data, 2)
        
        debug("Send fly-by-wire", 4)
        if self.headless:
            return
        
        for key, value in data.items():
            print key + ": " + str(value)
            if value == "None":
                value = None;
            
            self.vessel.run_command(key, value)

def main():
    a = arduino()
    
    while a.init() == False:
        time.sleep(10)
        debug("Restarting countdown.", 1)
    
    debug("\nWaiting for input:", 2)
    while 1:
        a.do()

@atexit.register
def stats():
    global sequence
    global retransmits
    
    print ""
    print ""
    print "=======[ Stats ]======="
    print "Updates:       %s" % sequence
    print "Retransmits:   %s" % retransmits
    if sequence > 0:
        print "Percentage:    %.2f%%" % (float(retransmits)*100/sequence)
    if time_count > 0 and time_sum > 0:
        print ""
        print "Rate:          %.2fms" % (float(time_sum)*1000/time_count)
        print "Frequency:     %.2fHz" % (1/(float(time_sum)/time_count))

if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)


