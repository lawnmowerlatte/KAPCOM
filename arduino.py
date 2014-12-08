#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# This module interfaces with a connected Arduino via serial connection
# and an API library for communication with Kerbal Space Program. This
# has been initially written to use the Telemachus API library with the
# Telemachus WebSocket API, but is designed to be modular enough that it
# could be replaced in the future without needing to rewrite this library.

import time
import serial
import os
import linecache
import math
import pyksp

class arduino:
    """Creates an interface between the Arduino serial connection and Telemachus library."""
    #port
    #serial
    #baud
    #vessel
    
    subscriptions = {
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
    
    def __init__(self, port="/dev/tty.usbmodem1411", baud=9600):
        """Takes an API object, serial port and baudrate and creates a new Arduino object."""
        self.port = port
        self.baud = baud
        
        self.vessel = pyksp.ActiveVessel()
        for subscription in self.subscriptions:
            self.vessel.subscribe(subscription)
            
        self.vessel.start()
        time.sleep(1)
        
        self.serial = serial.Serial(
            port=self.port,
            baudrate=self.baud)

    def hex2float(self, hex):
        max = 16**len(hex)
        mid = (max+1)/2
        val = int(hex, 16)
        val = (val - mid)*1.0/mid*1.0
        return val

    def parse_input(self, input):
        """Read the byte string from Arduino and send commands appropriately"""
        pitch   = self.hex2float(input[0:2])
        yaw     = self.hex2float(input[2:4])
        roll    = self.hex2float(input[4:6])
        x       = self.hex2float(input[6:8])
        y       = self.hex2float(input[8:10])
        z       = self.hex2float(input[10:12])
        
        self.vessel.set_6dof(pitch, yaw, roll, x, y, z)
        pass
    
    def api2hex(self, string, length):
        return hex(int(self.vessel.get(string)))[2:].zfill(length)
    
    def compile_output(self):
        """Return byte string of the output"""
        
        output = "O: "
        output += self.api2hex("vessel_altitude", 10)
        output += self.api2hex("vessel_apoapsis", 10)
        output += self.api2hex("vessel_periapsis", 10)
        output += self.api2hex("vessel_velocity", 10)
        output += self.api2hex("vessel_inclination", 4)
        
        # Handle cases where radar altimeter is unavailable
        alt = self.vessel.get("vessel_asl_height")
        if int(alt) is -1:
            alt = 0
        output += hex(int(alt))[2:].zfill(4)
        
        output += hex(int(self.vessel.get("resource_ox_current")/self.vessel.get("resource_ox_max")))[2:].zfill(2)
        output += hex(int(self.vessel.get("resource_mp_current")/self.vessel.get("resource_mp_max")))[2:].zfill(2)
        output += hex(int(self.vessel.get("resource_ox_current")/self.vessel.get("resource_ox_max")))[2:].zfill(2)
        output += hex(int(self.vessel.get("resource_ec_current")/self.vessel.get("resource_ec_max")))[2:].zfill(2)
        
        output += hex(self.vessel.get("sas_status"))[2:].zfill(1)
        output += hex(self.vessel.get("rcs_status"))[2:].zfill(1)
        output += hex(self.vessel.get("action_group_light"))[2:].zfill(1)
        output += hex(self.vessel.get("action_group_gear"))[2:].zfill(1)
        output += hex(self.vessel.get("action_group_brake"))[2:].zfill(1)
        
        return output
        
    def send_output(self, inputline):
        if inputline:
            self.serial.write(inputline + '\n')
        else:
            print "No input..."


print 'Starting Python listener...'
print 'Warming up the Arduino...'
time.sleep(2)
print 'Listening:'

a = arduino()
a.vessel.run_command("toggle_fbw", "1")
buffer = ""
inputs = ""

while 1:
    input = ""
    
    time.sleep(1)
    buffer = buffer + a.serial.read(a.serial.inWaiting())
    #print buffer
    
    if '\n' in buffer:
        lines = buffer.split('\n')
        
        if len(lines) > 0:
            for line in lines[:-1]:
                if "I: " in line:
                    input = line[3:]
                else:
                    print line
            buffer = lines[-1]
    
    if len(input) is 13:
        print "Sending input: " + input
        a.parse_input(input)
        #a.send_output(a.compile_output())
    #else:
        #print "Bad input: " + input
    
    
    
        
    
    

