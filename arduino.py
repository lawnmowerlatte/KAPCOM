#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# This module interfaces with a connected Arduino via serial connection
# and an API library for communication with Kerbal Space Program. This
# has been initially written to use the Telemachus API library with the
# Telemachus WebSocket API, but is designed to be modular enough that it
# could be replaced in the future without needing to rewrite this library.

debug = 5

import time
import serial
import os
import linecache
import math
import pyksp
import json

def debug(message, level=debug):
    if level <= debug:
        print message

class arduino:
    """Creates an interface between the Arduino serial connection and Telemachus library."""
    
    # Use this for simulation and debugging
    # This overrides the serial port with input from the interactive shell
    interactive = True
    
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
        
        self.vessel = pyksp.ActiveVessel()
        for subscription in self.subscriptions:
            self.vessel.subscribe(subscription)
            
        if not self.interactive:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud)
        else:
            debug("Using shell input", 1)
    
    def init(self):
        debug("Starting telemetry.", 1)
        self.vessel.start()
        time.sleep(1)
        
        if self.ready():
            debug("Waiting for Arduino.", 1)
            while not self.interactive and self.readSerial() != "ONLINE":
                time.sleep(1)
            debug("Waiting for calibration.", 1)
            while not self.interactive and self.readSerial() != "CALIBRATING":
                time.sleep(1)
            debug("Waiting for ready state.", 1)
            while not self.interactive and self.readSerial() != "READY":
                time.sleep(1)
        
            debug("All stations are go.", 1) 
            return True           
        else:
            debug("We have a hold for launch.", 1)
            return False
            
        
    def readSerial(self):
        """Read a line from serial"""
        if self.interactive:
            line = raw_input("> ")
        else:
            while '\n' not in buffer:
                buffer = buffer + self.serial.read(self.serial.inWaiting())
            
            lines = buffer.split('\n')
        
            if len(lines) > 0:
                for line in lines[:-1]:
                    if line is "READY":
                        debug("Arduino has reset. Restarting.", 1)
                        main()
                    else:
                        print line
                    
                    buffer = lines[-1]
            
        return line
    
    def writeSerial(self, line):
        """Write a line to serial"""
        if self.interactive:
            print "< " + line
        else:
            self.serial.write(line)
     
    def readOutput(self):
        """Read Telemachus telemetry"""
        debug("Read telemetry", 4)
        
        json = self.toJSON()
        return json
    
    def toJSON(self):
        """Return JSON string of the output"""
        debug("Generate JSON", 4)
        
        json.dumps(
            {
                "vessel_altitude": self.vessel.get("vessel_altitude"),
                "vessel_apoapsis": self.vessel.get("vessel_apoapsis"),
                "vessel_periapsis": self.vessel.get("vessel_periapsis"),
                "vessel_velocity": self.vessel.get("vessel_velocity"),
                "vessel_inclination": self.vessel.get("vessel_inclination"),
                
                "resource_ox_current": self.vessel.get("resource_ox_current"),
                "resource_ox_max": self.vessel.get("resource_ox_max"),
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
                
            }
        )
    
    def sendOutput(self, json):
        """Send JSON data to Arduino"""
        debug("Send output", 4)
        
        if json:
            self.writeSerial(json + '\n')
        else:
            debug("< No JSON data to send", 1)
    
    def readInput(self):
        """Poll Arduino for line of input containing JSON data"""
        debug("Read input", 4)
        
        json = self.readSerial()
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
        
        self.vessel.run_command("toggle_fbw", "1")
        ## Needs work...
     
    # State based methods
    def online(self):
        json = self.readOutput()
        self.sendOutput(json)
        data = self.readInput()
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

    def state(self, state):
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
        else:
            debug("Unhandled game state: " + str(state), 1)
        
    def ready(self):
        connectionState = self.vessel.test_connection()
        debug("Connection state: " + str(connectionState), 5)
        
        gameState = self.vessel.get("pause_state")
        debug("Telemachus state: " + str(gameState), 5)
        
        if connectionState and gameState == 0:
            debug("Status: GO", 5)
            return True
        else:
            debug("Status: NO GO", 1)
            return False
        
    def runStatus(self):
        gameState = self.vessel.get("pause_state")
        self.state(gameState)

def main():
    a = arduino()
    
    while a.init() == False:
        time.sleep(10)
        debug("Restarting countdown.", 1)
    
    while 1:
        a.runStatus()
        
        
main()