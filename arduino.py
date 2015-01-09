#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# This module interfaces with a connected Arduino via serial connection
# and an API library for communication with Kerbal Space Program. This
# has been initially written to use the Telemachus API library with the
# Telemachus WebSocket API, but is designed to be modular enough that it
# could be replaced in the future without needing to rewrite this library.

debug = 5

import sys
import socket
import time
import serial
import os
import linecache
import math
import pyksp
import json

def debug(message, level=debug, newline=True):
    if level <= debug:
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
    headless = False
    
    buffer = ""
    
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
    
    def __init__(self, port="/dev/tty.usbmodem1411", baud=9600):
        """Takes an API object, serial port and baudrate and creates a new Arduino object."""
        self.port = port
        self.baud = baud
        
        if not self.headless:
            self.vessel = pyksp.ActiveVessel()
            for subscription in self.subscriptions:
                self.vessel.subscribe(subscription)
        else:
            debug("Using dummy telemetry", 4)
            
        if not self.interactive:
            try:
                self.serial = serial.Serial(
                    port=self.port,
                    baudrate=self.baud)
            except:
                debug("No serial port found.")
                raw_input("Press [Enter] to retry.")
                main()
        else:
            debug("Using shell input", 4)
    
    # Serial manipulation methods
    def readSerial(self):
        """Read a line from serial"""
        if self.interactive:
            line = raw_input("> ")
        else:
            line = self.serial.readline()
            
            #while '\n' not in self.buffer:
            #    self.buffer = self.buffer + self.serial.read(self.serial.inWaiting())
            #    if '\r' in self.buffer:
            #        print "x"
            
            #lines = self.buffer.split('\n')
        
            #if len(lines) > 0:
            #    for line in lines[:-1]:
            #        if line is "READY":
            #            debug("Arduino has reset. Restarting.", 1)
            #            main()
            #        else:
            #            # print line
            #            debug("-", 1, False)
                   
            #        self.buffer = lines[-1]
            
        return line
    
    def writeSerial(self, line):
        """Write a line to serial"""
        if self.interactive:
            print "< " + line
        else:
            self.serial.write(line)
    
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
        while not self.interactive and "ONLINE" not in self.readSerial():
            i = self.tick()
            if i is False:
                self.hold("Timeout while waiting for Arduino.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 2)
        
        debug("Calibration...", 2, False)
        self.timer(10)
        while not self.interactive and "CALIBRATING" not in self.readSerial():
            i = self.tick()
            if i is False:
                self.hold("Timeout while calibrating.")
                return False
            else:
                debug(".", 3, False)
        debug("Go", 1)
        
        debug("Fly by wire...", 2, False)
        self.timer(5)
        while not self.interactive and "READY" not in self.readSerial():
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
        json = self.readOutput()
        self.sendOutput(json)
        data = self.readInput()
        
        if data:
            self.sendInput(data)

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
            time.sleep(5)
            currentState = self.vessel.get("pause_state")
        print "Unpaused"

    def menu(self):
        print "Waiting for vessel"
        currentState = self.vessel.get("pause_state")
        while currentState == None:
            time.sleep(5)
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
            self.writeSerial(json + "\r\n")
        else:
            debug("< No JSON data to send", 1)
    
    def readInput(self):
        """Poll Arduino for line of input containing JSON data"""
        debug("Read input", 4)
        
        json = self.readSerial()
        debug(json, 5)
        data = self.fromJSON(json)
        return data
    
    def fromJSON(self, jdata):
        """Parse JSON input from Arduino"""
        debug("Parse JSON", 4)
        
        try:
            data = json.loads(jdata)
            return data
        except:
            debug("No JSON data found in string: " + str(jdata))
        
    
    def sendInput(self, data):
        """Send Telemachus commands based on input"""
        debug("Send fly-by-wire", 4)
        
        if self.headless:
            return
        
        for key, value in data.items():
            print key + ": " + str(value)
            self.vessel.run_command(key, value)

def main():
    a = arduino()
    
    while a.init() == False:
        time.sleep(10)
        debug("Restarting countdown.", 1)
    
    while 1:
        a.do()
        
        
main()