#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# and a physical game controller based on Arduino hardware. The Arduino
# and Kerbal Space Program interactions are handled in separate classes,
# this module connects them and interfaces with various hardware driver
# classes.

import sys
import socket
import time
import atexit
import json

# sys.path.append("./pyksp")
import pyksp

from arduino import arduino
from pin import *
from mod import mod
from joy import joy
from bargraph import bargraph
from display import display

cycles=0
duration=0

debugger = 4
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
        "resource_sf_max",
        "resource_sf_current",
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
    
    port        =   None
    baud        =   None
    host        =   None
    sock        =   None
    
    configurationFile   =   'kapcom.json'
    
    # Set default values
    defaults    =   {
        'port'  :   None,
        'baud'  :   115200,
        'host'  :   "127.0.0.1",
        'sock'  :   8085    }
    
    def __init__(self, port=None, baud=None, host=None, sock=None):
        """Takes serial port, baudrate and socket information and creates the KAPCOM object."""
        def loadDefaults(configuration, parameter, argument):
            try:
                config          =   configuration[parameter]
            except:
                config          =   None
            
            try:
                default         =   self.defaults[parameter]
            except:
                default         =   None
        
            if argument is None:
                if config is None:
                    setattr(self, parameter, default)
                else:
                    setattr(self, parameter, config)
            else:
                setattr(self, parameter, argument)
        
        with open(self.configurationFile, 'r') as file:
            j   =   json.load(file)
        
        for list in {   ('port', port),
                        ('baud', baud),
                        ('host', host),
                        ('sock', sock)     }:
            loadDefaults(j, list[0], list[1])
        file.close()
        
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
            hold("Timeout while waiting for hardware.")
            return False
        
        debug("Configuration...", 2, False)
        try:
            self.configure()
        except:
            hold("Failed to read configuration file.")
            return False
        try:
            # Create objects
            debug("Go", 2)
        except:
            hold("Failed to create data models.")
            return False
         
        debug("Telemetry...", 2, False)
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))
            if r == 0:
                self.vessel.start()
                time.sleep(1)
            else:
                hold("Unable to connect to telemetry")
                return False
        for i in range(1, 20):
            if self.ready():
                debug("Go", 2)
                break
            wait()
        else:
            self.hold("Timeout while waiting for telemetry.")
            return False
        
        debug("All stations are go.", 1)
        self.sendFlyByWire("toggle_fbw", "1")
        return True
        
    def configure(self):
        self.inputs      =   []
        self.outputs     =   []
        self.bargraphs   =   []
        self.displays    =   []
        
        def loadObject(configuration, list):
            try:
                type = globals().get(configuration['type'])
            except AttributeError:
                print 'Type not found "%s" (%s)' % (self._format, arg)
            else:
                configuration.pop('type')
                if not configuration.get('options'):
                    configuration['options']    =   None
                list.append(type(self.arduino, **configuration))
        
        # Open the configuration file
        with open(self.configurationFile, 'r') as file:
            j   =   json.load(file)
        
        # Load the joysticks
        for joyIndex in j['joys']:
            if joyIndex['name'] == 'Joy0':
                self.joy0 = joy(self.arduino, **joyIndex)
            elif joyIndex['name'] == 'Joy1':
                self.joy1 = joy(self.arduino, **joyIndex)
            else:
                print "Unknown joystick: " + joyIndex['name']
        
        # Load all the objects!
        for key, value in { 'inputs'      : self.inputs,
                            'outputs'     : self.outputs,
                            'bargraphs'   : self.bargraphs,
                            'displays'    : self.displays     }.iteritems():
            for configuration in j[key]:
                try:
                    type = configuration['type']
                    loadObject(configuration, value)
                except:
                    print "No type found. Skipping."
                    print configuration
                
        file.close()
        
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

        # self.sendFlyByWire("toggle_fbw", "1")
        self.sendFlyByWire("six_dof", self.joy0.toString() + "," + self.joy1.toString())
        
        # Iterate across inputs
        for i in self.inputs:
            # Get the value from hardware
            i.update()
            value = i.toString()
            
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
            return self.vessel.get(api)
        else:
            return 0
    
    def sendFlyByWire(self, api, value):
        # If missing data, do nothing
        if api == "" or value == "":
            return
        
        print api + "=" + str(value)
        
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