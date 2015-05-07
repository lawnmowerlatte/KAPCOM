#! /usr/bin/python

# This module allows programs to interface with Kerbal Space Program
# and a physical game controller based on Arduino hardware. The Arduino
# and Kerbal Space Program interactions are handled in separate classes,
# this module connects them and interfaces with various hardware driver
# classes.

import sys
import os
import getopt
import socket
import time
import atexit
import json

sys.path.append(os.getcwd() + "/pyksp")
import pyksp

from arduino import arduino
from pin import *
from mod import mod
from joy import joy
from bargraph import bargraph
from display import display


_cycles = 0
_duration = 0
_debug = 6


def debug(message, level=_debug, newline=True):
    """Debugging log message"""
    
    if level <= _debug:
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

    # Define subscriptions for PyKSP to use
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

    # Define empty lists for objects
    joys        =   []
    inputs      =   []
    outputs     =   []
    bargraphs   =   []
    displays    =   []

    # Define configuration options as blanks
    conf        =   None
    port        =   None
    baud        =   None
    host        =   None
    sock        =   None
    headless    =   None

    # Define empty objects
    arduino     =   None
    joy0        =   None
    joy1        =   None
    
    # Set default values
    defaults = {
        'conf':     "kapcom.json",
        'port':     None,
        'baud':     115200,
        'host':     "127.0.0.1",
        'sock':     8085,
        'headless': False
    }
    
    def __init__(self, conf=None, port=None, baud=None, host=None, sock=None, headless=False):
        """Takes serial port, baud rate and socket information and creates the KAPCOM object."""

        def load_configuration(parameter_name, argument_value, configuration_value, default_value):
            """Loads the object configuration, taking into account arguments, the configuration file and defaults"""

            # If argument is set...
            if argument_value is not None:
                # Use the argument
                setattr(self, parameter_name, argument_value)
                debug("Using argument value '" + str(argument_value) + "' for " + parameter_name + ".", 6)
            else:
                # Otherwise, if it's in the configuration file...
                if configuration_value is not None:
                    # Use the configuration value
                    setattr(self, parameter_name, configuration_value)
                    debug("Using configuration value '" + str(configuration_value) + "' for " + parameter_name + ".", 6)
                else:
                    # Otherwise, use the default
                    setattr(self, parameter_name, default_value)
                    debug("Using default value '" + str(default_value) + "' for " + parameter_name + ".", 6)

        # Get the configuration file to use
        load_configuration("conf", conf, None, self.defaults.get("conf"))

        # Open the file and load the JSON data
        with open(self.conf, 'r') as config_file:
            config_json = json.load(config_file)

            # For the list of default
            for parameter, default_value in self.defaults.iteritems():
                argument_value = eval(parameter)
                configuration_value = config_json.get(parameter)

                load_configuration(parameter, argument_value, configuration_value, default_value)

        # Close the configuration file
        config_file.close()

        # If we are not headless, connect to Telemachus via PyKSP
        if not self.headless:
            # Connect
            self.vessel = pyksp.ActiveVessel(url=self.host + ":" + str(self.sock))
            # Subscribe
            for subscription in self.subscriptions:
                self.vessel.subscribe(subscription)
        else:
            debug("Using dummy telemetry", 3)
    
    # Initialization and Readiness methods
    def initialize(self):
        """Attempt to connect to Arduino and Telemachus"""

        # We hit an error, print a message and try again
        def hold(message):
            debug("We have a hold for launch.", 1)
            debug(message, 2)

        # We're waiting...
        def wait():
            debug(".", 3, False)
            time.sleep(1)

        # Connect to Arduino
        debug("Fly by wire...", 2, False)
        self.arduino = arduino(self.port, self.baud)
        if self.arduino is None:
            hold("Hardware failed to initialize.")
            return False
        debug("Go", 2)

        # Configure
        debug("Configuration...", 2, False)
        try:
            self.configure()
        except:
            hold("Failed to read configuration file.")
            return False
        debug("Go", 2)

        # If we're not headless, connect
        if not self.headless:
            debug("Telemetry...", 2, False)

            # Connect to the Telemachus socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))

            # If we can connect, start the vessel
            if r == 0:
                self.vessel.start()
            else:
                hold("Unable to connect to telemetry")
                return False

        # Check that the connection is ready
        for i in range(1, 20):
            if self.ready():
                debug("Go", 2)
                break
            wait()
        else:
            self.hold("Timeout while waiting for telemetry.")
            return False
        
        debug("All stations are go.", 1)
        return True
        
    def configure(self):
        self.inputs = []
        self.outputs = []
        self.bargraphs = []
        self.displays = []
        
        def load_object(object_configuration, object_list):
            try:
                object_type = globals().get(configuration['type'])
                debug("Found type: " + configuration['type'], 6)
            except AttributeError:
                debug("Type not found in '" + object_configuration + "'", 4)
                return

            object_configuration.pop('type')
            if not object_configuration.get('options'):
                object_configuration['options'] = None
                debug("No options found, adding blank", 6)

            print object_configuration
            object_list.append(object_type(self.arduino, **object_configuration))

        
        # Open the configuration file
        with open(self.conf, 'r') as file:
            j = json.load(file)
        
        # Load the joysticks
        for joyIndex in j['joys']:
            if joyIndex['name'] == 'Joy0':
                self.joy0 = joy(self.arduino, **joyIndex)
                debug("Adding Joy0", 5)
            elif joyIndex['name'] == 'Joy1':
                self.joy1 = joy(self.arduino, **joyIndex)
                debug("Adding Joy1", 5)
            else:
                debug("Unknown joystick: " + joyIndex['name'], 4)
        
        # Load all the objects!
        debug("Loading objects:", 3)
        for key, value in {'inputs':       self.inputs,
                           'outputs':      self.outputs,
                           'bargraphs':    self.bargraphs,
                           'displays':     self.displays
        }.iteritems():
            debug("Loading " + key + ": ", 3)
            for configuration in j[key]:
                debug("Loading object '" + configuration['name'] + "': ", 4)
                load_object(configuration, value)
                debug("Success!", 4)

        file.close()
        
    def ready(self):
        """Attempt to connect to Telemachus."""
        
        state = False

        # If we're not headless, check the socket
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))
            if r == 0:
                # If there's a good connection, get
                state = self.vessel.test_connection()
                debug("Connection state: " + str(state), 5)
        # Otherwise just return True
        else:
            state = True
        
        return state

    def do(self):
        """Act based on the game state."""
        states = ["Online", "Paused", "Antenna is unpowered", "Antenna is off", "No antenna found", "No vessel"]

        if not self.headless and self.ready():
            try:
                state = self.vessel.get("pause_state")
                state = int(state)
            except (ValueError, TypeError):
                if state is None:
                    state = 5
                else:
                    debug("Unhandled state: " + str(state), 3)

            if state > 5:
                debug("Unhandled state: " + str(state), 3)

            debug("Telemachus state: " + str(state) + ": " + states[int(state)], 5)
        else:
            state = 0

        if state == 0:
            self.online()
        else:
            while True:
                if state != self.vessel.get("pause_state"):
                    break
                time.sleep(1)
    
    # Game state methods
    def online(self):
        """Update game and hardware."""
        global _cycles
        global _duration
        
        start = time.time()
        
        self.update()
        
        end = time.time()
        d = end - start
        _duration = ((_duration * _cycles) + d)/(_cycles+1)
        _cycles += 1

    def update(self):
        if self.joy0 is not None and self.joy1 is not None:
            # Update joysticks and send data
            self.joy0.update()
            self.joy1.update()

            six_dof = self.joy0.toString() + "," + self.joy1.toString()
            if six_dof != "0,0,0,0,0,0":
                self.send_flybywire("toggle_fbw", "1")
                self.send_flybywire("six_dof", six_dof)
            else:
                self.send_flybywire("toggle_fbw", "0")
        
        # Iterate across inputs
        for i in self.inputs:
            # Get the value from hardware
            i.update()
            value = i.toString()
            
            # If it had changed
            if i.changed():
                # Send the update
                self.send_flybywire(i.api, value)
            
        # Set the outputs
        for o in self.outputs:
            o.set(self.get_telemetry(o.api))
            
        # Set the bargraphs
        for b in self.bargraphs:
            b.setMax(self.get_telemetry(b._max_api))
            b.set(self.get_telemetry(b.api))
        
        # Set the displays
        for d in self.displays:
            d.set(self.get_telemetry(d.api))
        
    def get_telemetry(self, api):
        if not self.headless:
            if len(api) > 0:
                return self.vessel.get(api)
        else:
            return 0
    
    def send_flybywire(self, api, value):
        # If missing data, do nothing
        if api == "" or value == "":
            return
        
        print api + "=" + str(value)
        
        # If we're connected, send the command
        if not self.headless:
            self.vessel.run_command(api, value)
        
def usage():
    """Print out a usage message"""
    
    print "%s [-h] [-d level|--debug=level] [-c file|--config=file]" % sys.argv[0]

def main(argv):
    """Create KAPCOM object, initialize and run."""

    filename = None

    try:
        opts, args = getopt.getopt(argv, "hd:c:", ["help", "debug=", "config="] )
    except getopt.GetoptError:
        usage()
        exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-d", "--debug"):
            global _debug
            _debug = arg
        elif opt in ("-c", "--config"):
            filename = arg
    
    if filename is None:
        k = kapcom()
    else:
        k = kapcom(filename)
    
    while not k.initialize():
        time.sleep(10)
        debug("Restarting countdown.", 1)
    
    debug("\nReady for input:", 2)
    while 1:
        k.do()


@atexit.register
def stats():
    """Calculate statistics based on duration of updates."""
    global _duration
    global _cycles
    
    print ""
    print ""
    print "=======[ Stats ]======="
    print "Cycles:        %s"       % _cycles
    
    if _cycles > 0:
        print "Rate:          %.2fms"   % (float(_duration)*1000)
        print "Frequency:     %.2fHz"   % (1/float(_duration))


if __name__ == "__main__":    
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)