#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# and a physical game controller based on Arduino hardware. The Arduino
# and Kerbal Space Program interactions are handled in separate classes,
# this module connects them and interfaces with various hardware driver
# classes.

import sys
import socket
import time
import pyksp
import atexit
import json

from arduino import arduino
from pin import *
from mod import mod
from joy import joy
from bargraph import bargraph
from display import display

cycles=0
duration=0

debugger = 6
def debug(message, level=debugger, newline=True):
    """Debugging log message"""
    
    if level <= debugger:
        if newline:
            print(message) 
        else:
            sys.stdout.write(message)

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
    
class kapcom(object):
    """Creates an interface between the Arduino serial connection and Telemachus library."""
    
    # Use these for simulation and debugging
    # This overrides the serial port with input from the interactive shell
    interactive = False
    # This overrides the Telemachus port with static simulated input
    headless = True
    
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
    
    inputs      =   []
    outputs     =   []
    bargraphs   =   []
    displays    =   []
    
    def __init__(self, port=None, baud=250000, host="127.0.0.1", sock=8085):
        """Takes serial port, baudrate and socket information and creates the KAPCOM object."""
        
        self.port = port
        self.baud = baud
        self.host = host
        self.sock = sock
        
        if not self.headless:
            self.vessel = pyksp.ActiveVessel()
            for subscription in self.subscriptions:
                self.vessel.subscribe(subscription)
        else:
            debug("Using dummy telemetry", 3)
    
    
    # Initialization and Readiness methods
    def start(self):
        """Attempt to connect to Arduino and Telemachus"""
        
        def hold(message):
            debug("We have a hold for launch.", 1)
            debug(message, 2)
        def wait():
            debug(".", 3, False)
            time.sleep(1)
        
        debug("Telemetry...", 2, False)
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))
            if r == 0:
                self.vessel.start()
                time.sleep(1)
            else:
                self.hold("Unable to connect to telemetry")
                return False
        for i in range(1, 20):
            if self.ready():
                debug("Go", 2)
                break
            wait()
        else:
            self.hold("Timeout while waiting for telemetry.")
            return False
        
        debug("Fly by wire...", 2, False)
        for i in range(1, 20):
            try:
                self.arduino = arduino(self.port, self.baud)
            except:
                wait()
            else:
                debug("Go", 2)
                break
        else:
            self.hold("Timeout while waiting for telemetry.")
            return False
        
        debug("Configuration...", 2, False)
        try:
            # Parse configuration
            pass
        except:
            self.hold("Failed to read configuration file.")
            return False
        try:
            # Create objects
            debug("Go", 2)
        except:
            self.hold("Failed to create data models.")
            return False
        
        # Set some static shit
        self.joy0 = joy(self.arduino, "Joy0", 0xA0, 0xA1, 0xA2, 0xA3)
        self.joy1 = joy(self.arduino, "Joy1", 0xA4, 0xA5, 0xA6, 0xA7)
        
        self.inputs.append(analogIn(self.arduino, "Throttle", "set_throttle", 0xA8))
        
        self.inputs.append(mod(self.arduino, "Abort", "abort", 0xA9, 0xAB, 0xAA))
        self.inputs.append(mod(self.arduino, "Stage", "stage", 0xAC, 0xAE, 0xAD))
        
        self.inputs.append(digitalIn(self.arduino, "Map", "toggle_map", 8))
        
        self.inputs.append(digitalIn(self.arduino, "SAS", "sas", 22))
        self.inputs.append(digitalIn(self.arduino, "RCS", "ras", 26))
        self.inputs.append(digitalIn(self.arduino, "Light", "light", 30))
        self.inputs.append(digitalIn(self.arduino, "Gear", "gear", 34))
        self.inputs.append(digitalIn(self.arduino, "Break", "brake", 38))
        
        self.inputs.append(digitalIn(self.arduino, "Action Group 1", "action_group_1", 23))
        self.inputs.append(digitalIn(self.arduino, "Action Group 2", "action_group_2", 25))
        self.inputs.append(digitalIn(self.arduino, "Action Group 3", "action_group_3", 27))
        self.inputs.append(digitalIn(self.arduino, "Action Group 4", "action_group_4", 29))
        self.inputs.append(digitalIn(self.arduino, "Action Group 5", "action_group_5", 31))
        self.inputs.append(digitalIn(self.arduino, "Action Group 6", "action_group_6", 33))
        self.inputs.append(digitalIn(self.arduino, "Action Group 7", "action_group_7", 35))
        self.inputs.append(digitalIn(self.arduino, "Action Group 8", "action_group_8", 37))
        self.inputs.append(digitalIn(self.arduino, "Action Group 9", "action_group_9", 39))
        self.inputs.append(digitalIn(self.arduino, "Action Group 10", "action_group_10", 41))
        
        self.inputs.append(digitalIn(self.arduino, "Warp -", "", 42))
        self.inputs.append(digitalIn(self.arduino, "Warp +", "", 43))
        self.inputs.append(digitalIn(self.arduino, "Ship -", "", 44))
        self.inputs.append(digitalIn(self.arduino, "Ship +", "", 45))
        self.inputs.append(digitalIn(self.arduino, "Camera -", "", 46))
        self.inputs.append(digitalIn(self.arduino, "Camera +", "", 47))
        
        self.outputs.append(digitalOut(self.arduino, "SAS Status", "sas_status", 24))
        self.outputs.append(digitalOut(self.arduino, "SAS Status", "sas_status", 28))
        self.outputs.append(digitalOut(self.arduino, "Light Status", "action_group_light", 32))
        self.outputs.append(digitalOut(self.arduino, "Gear Status", "action_group_gear", 36))
        self.outputs.append(digitalOut(self.arduino, "Break Status", "action_group_brake", 40))
        
        self.bargraphs.append(bargraph(self.arduino, "LF", "resource_lf_current", 0))
        self.bargraphs.append(bargraph(self.arduino, "OX", "resource_ox_current", 1))
        self.bargraphs.append(bargraph(self.arduino, "EL", "resource_ec_current", 2))
        self.bargraphs.append(bargraph(self.arduino, "MP", "resource_mp_current", 3))
        self.bargraphs.append(bargraph(self.arduino, "SF", "resource_sf_current", 4))
        
        self.displays.append(display(self.arduino, "ALT", "vessel_altitude", 0))
        self.displays.append(display(self.arduino, "VEL", "vessel_orbital_velocity", 1))
        self.displays.append(display(self.arduino, "AP", "vessel_apoapsis", 2))
        self.displays.append(display(self.arduino, "PE", "vessel_periapsis", 3))
        self.displays.append(display(self.arduino, "RAD", "vessel_asl_height", 4))
        
        j    =   { 'joys'        :   [
                            {   "name"    :   "Joy0",
                                "x"       :   0xA0,
                                "y"       :   0xA1,
                                "z"       :   0xA2,
                                "button"  :   0xA3,
                                "options" :   None
                            },
                            {   "name"    :   "Joy1",
                                "x"       :   0xA4,
                                "y"       :   0xA5,
                                "z"       :   0xA6,
                                "button"  :   0xA7,
                                "options" :   None
                            }],
                      'inputs'      :   [
                            {   "type"    :   "analogIn",
                                "name"    :   "Throttle",
                                "api"     :   "set_throttle",
                                "pin"     :   0xA8
                            },
                            {   "type"    :   "analogIn",
                                "name"    :   "Throttle",
                                "api"     :   "set_throttle",
                                "pin"     :   0xA8
                            },
                            {   "type"    :   "mod",
                                "name"    :   "Abort",
                                "api"     :   "abort",
                                "pin"     :   [ 0xA9, 0xAA, 0xAB ]
                            },
                            {   "type"    :   "mod",
                                "name"    :   "Stage", 
                                "api"     :   "stage",
                                "pin"     :   [ 0xAC, 0xAD,0xAE ]
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Map",
                                "api"     :   "toggle_map",
                                "pin"     :   8
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "SAS",
                                "api"     :   "sas",
                                "pin"     :   22
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "RCS",
                                "api"     :   "ras",
                                "pin"     :   26
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Light",
                                "api"     :   "light",
                                "pin"     :   30
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Gear",
                                "api"     :   "gear",
                                "pin"     :   34
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Break",
                                "api"     :   "brake",
                                "pin"     :   38
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 1",
                                "api"     :   "action_group_1",
                                "pin"     :   23
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 2",
                                "api"     :   "action_group_2",
                                "pin"     :   25
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 3",
                                "api"     :   "action_group_3",
                                "pin"     :   27
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 4",
                                "api"     :   "action_group_4",
                                "pin"     :   29
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 5",
                                "api"     :   "action_group_5",
                                "pin"     :   31
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 6",
                                "api"     :   "action_group_6",
                                "pin"     :   33
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 7",
                                "api"     :   "action_group_7",
                                "pin"     :   35
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 8",
                                "api"     :   "action_group_8",
                                "pin"     :   37
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 9",
                                "api"     :   "action_group_9",
                                "pin"     :   39
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Action Group 10",
                                "api"     :   "action_group_10",
                                "pin"     :   41
                            },
        
                            {   "type"    :   "digitalIn",
                                "name"    :   "Warp -",
                                "api"     :   "",
                                "pin"     :   42
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Warp +",
                                "api"     :   "",
                                "pin"     :   43
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Ship -",
                                "api"     :   "",
                                "pin"     :   44
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Ship +",
                                "api"     :   "",
                                "pin"     :   45
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Camera -",
                                "api"     :   "",
                                "pin"     :   46
                            },
                            {   "type"    :   "digitalIn",
                                "name"    :   "Camera +",
                                "api"     :   "",
                                "pin"     :   47
                            }],
                        'outputs'       :   [
                            {   "type"    :   "digitalOut",
                                "name"    :   "SAS Status",
                                "api"     :   "sas_status",
                                "pin"     :   24
                            },
                            {   "type"    :   "digitalOut",
                                "name"    :   "SAS Status",
                                "api"     :   "sas_status",
                                "pin"     :   28
                            },
                            {   "type"    :   "digitalOut",
                                "name"    :   "Light Status",
                                "api"     :   "action_group_light",
                                "pin"     :   32
                            },
                            {   "type"    :   "digitalOut",
                                "name"    :   "Gear Status",
                                "api"     :   "action_group_gear",
                                "pin"     :   36
                            },
                            {   "type"    :   "digitalOut",
                                "name"    :   "Break Status",
                                "api"     :   "action_group_brake",
                                "pin"     :   40
                            }],
                        'bargraphs'     :   [
                            {   "type"    :   "bargraph",
                                "name"    :   "LF",
                                "api"     :   "resource_lf_current",
                                "pin"     :   0
                            },
                            {   "type"    :   "bargraph",
                                "name"    :   "OX",
                                "api"     :   "resource_ox_current",
                                "pin"     :   1
                            },
                            {   "type"    :   "bargraph",
                                "name"    :   "EL",
                                "api"     :   "resource_ec_current",
                                "pin"     :   2
                            },
                            {   "type"    :   "bargraph",
                                "name"    :   "MP",
                                "api"     :   "resource_mp_current",
                                "pin"     :   3
                            },
                            {   "type"    :   "bargraph",
                                "name"    :   "SF",
                                "api"     :   "resource_sf_current",
                                "pin"     :   4
                            }],
                        'displays'      :   [
                            {   "type"    :   "display",
                                "name"    :   "ALT",
                                "api"     :   "vessel_altitude",
                                "pin"     :   0
                            },
                            {   "type"    :   "display",
                                "name"    :   "VEL",
                                "api"     :   "vessel_orbital_velocity",
                                "pin"     :   1
                            },
                            {   "type"    :   "display",
                                "name"    :   "AP",
                                "api"     :   "vessel_apoapsis",
                                "pin"     :   2
                            },
                            {   "type"    :   "display",
                                "name"    :   "PE",
                                "api"     :   "vessel_periapsis",
                                "pin"     :   3
                            },
                            {   "type"    :   "display",
                                "name"    :   "RAD",
                                "api"     :   "vessel_asl_height",
                                "pin"     :   4
                            }]
                    }
                  
        with open('kapcom.json', 'w') as file:
            json.dump(j, file, indent=4, separators=(',', ': '))
                    
        breakpoint()
         
                              
        debug("All stations are go.", 1) 
        return True
        
    
    def ready(self):
        """Attempt to connect to Telemachus."""
        
        connectionState = False
        
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))
            if r == 0:
                connectionState = self.vessel.test_connection()
                debug("Connection state: " + str(connectionState), 5)
        else:
            connectionState = True
        
        return connectionState

    def do(self):
        """Act based on the game state."""
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
        """Update game and hardware."""
        global cycles
        global duration
        
        start       = time.time()
        
        self.update()
        
        end         = time.time()
        d           = end - start
        duration    = ((duration * cycles) + d)/(cycles+1)
        cycles      += 1
         

    def paused(self):
        print "Paused"
        while self.vessel.get("pause_state") == 1:
            time.sleep(1)
        print "Unpaused"

    def unpowered(self):
        print "Antenna is unpowered"
        while self.vessel.get("pause_state") == 2:
            time.sleep(1)
    
    def off(self):
        print "Antenna is off"
        while self.vessel.get("pause_state") == 3:
            time.sleep(1)
        
    def missing(self):
        print "No antenna found"
        while self.vessel.get("pause_state") == 4:
            time.sleep(1)
       
    def menu(self):
        print "Waiting for vessel"
        while self.vessel.get("pause_state") == None:
            time.sleep(1)
        print "Vessel ready for connection"
        

    def update(self):
        # Update joysticks and send data
        self.joy0.update()
        self.joy1.update()
        self.sendFlyByWire("v.setPitchYawRollXYZ", self.joy0.toString() + "," + self.joy1.toString())
        
        # Iterate across inputs
        for i in self.inputs:
            # Get the value
            value = i.get()
            # If it had changed
            if i.changed():
                # Send the update
                self.sendFlyByWire(i.api, value)
            
        # Set the outputs
        for o in self.outputs:
            o.set(self.getTelemetry(o.api))
            
        # Set the bargraphs
        for b in self.bargraphs:
            b.set(self.getTelemetry(b.api))
        
        # Set the displays
        for d in self.displays:
            d.set(self.getTelemetry(d.api))
        
    def getTelemetry(self, api):
        if not self.headless:
            return self.getTelemetry(api)
        else:
            return 0
    
    def sendFlyByWire(self, api, value):
        # If missing data, do nothing
        if api == "" or value == "":
            return
        
        # If we're connected, send the command
        if not self.headless:
            self.vessel.run_command(api, value)
        
        
  
def main():
    """Create KAPCOM object, initialize and run."""
    k = kapcom()
    
    while k.start() == False:
        time.sleep(10)
        debug("Restarting countdown.", 1)
    
    debug("\nWaiting for input:", 2)
    while 1:
        k.do()

@atexit.register
def stats():
    """Calculate statistics based on duration of updates."""
    global duration
    global cycles
    
    print ""
    print ""
    print "=======[ Stats ]======="
    print "Cycles:        %s"       % cycles
    
    if cycles > 0:
        print "Rate:          %.2fms"   % (float(duration)*1000)
        print "Frequency:     %.2fHz"   % (1/float(duration))

if __name__ == "__main__":    
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)