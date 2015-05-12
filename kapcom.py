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
import logging

sys.path.append(os.getcwd() + "/pyksp")
import pyksp

from arduino import Arduino
# from pin import *
import pin
from mod import mod
from joy import Joy
from bargraph import Bargraph
from sevensegment import SevenSegment

_cycles = 0
_duration = 0

# Logging
_name = "KAPCOM"
_debug = logging.WARNING
log = logging.getLogger(_name)
log.setLevel(_debug)

longFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-10.10s]  %(message)s")
shortFormatter = logging.Formatter("[%(levelname)-8.8s]  %(message)s")

fileHandler = logging.FileHandler("logs/{0}/{1}.log".format("./", _name))
fileHandler.setFormatter(longFormatter)
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(shortFormatter)
log.addHandler(consoleHandler)


def breakpoint():
    """Python debug breakpoint."""
    
    from code import InteractiveConsole
    from inspect import currentframe
    try:
        import readline
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


class KAPCOM(object):
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

        # Define configuration options as blanks
        self.conf = None
        self.port = None
        self.baud = None
        self.host = None
        self.sock = None
        self.headless = None

        # Define empty objects
        self.arduino = None
        self.joy0 = None
        self.joy1 = None

        # Define empty lists for objects
        self.joys = []
        self.inputs = []
        self.outputs = []
        self.bargraphs = []
        self.displays = []

        self.flybywire = 0

        def set_configuration(parameter_name, argument, configuration, default):
            """Loads the object configuration, taking into account arguments, the configuration file and defaults"""

            # If argument is set...
            if argument is not None:
                # Use the argument
                setattr(self, parameter_name, argument)
                log.debug("Using argument value '" + str(argument) + "' for " + parameter_name + ".")
            else:
                # Otherwise, if it's in the configuration file...
                if configuration is not None:
                    # Use the configuration value
                    setattr(self, parameter_name, configuration)
                    log.debug("Using configuration value '" + str(configuration) + "' for " + parameter_name + ".")
                else:
                    # Otherwise, use the default
                    setattr(self, parameter_name, default)
                    log.debug("Using default value '" + str(default) + "' for " + parameter_name + ".")

        # Get the configuration file to use
        set_configuration("conf", conf, None, self.defaults.get("conf"))

        # Open the file and load the JSON data
        with open(self.conf, 'r') as config_file:
            config_json = json.load(config_file)

            # For the list of default
            for parameter, default_value in self.defaults.iteritems():
                argument_value = eval(parameter)
                configuration_value = config_json.get(parameter)

                set_configuration(parameter, argument_value, configuration_value, default_value)

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
            log.info("Using dummy telemetry")

        while not self.initialize():
            time.sleep(10)
            log.info("Restarting countdown.")
    
    # Initialization and Readiness methods
    def initialize(self):
        """Attempt to connect to Arduino and Telemachus"""
        # Connect to Arduino
        log.info("Initializing fly-by-wire system")
        self.arduino = Arduino(self.port, self.baud)
        if self.arduino is None:
            log.error("Hardware failed to initialize.")
            return False
        log.info("Fly-by-wire initialized")

        # Configure
        log.info("Reading configuration and creating objects")
        try:
            self.configure()
        except IOError:
            log.error("Failed to read configuration file.")
            return False
        log.info("Configuration successful")

        # If we're not headless, connect
        if not self.headless:
            log.info("Connecting to ship telemetry")

            # Connect to the Telemachus socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.sock))

            # If we can connect, start the vessel
            if r == 0:
                self.vessel.start()
            else:
                log.error("Unable to connect to telemetry")
                return False

        # Check that the connection is ready
        for i in range(1, 20):
            if self.ready():
                log.info("Connected to telemetry")
                break
            time.sleep(1)
        else:
            log.error("Timeout while waiting for telemetry.")
            return False
        
        log.info("All systems are go.")
        return True
        
    def configure(self):
        self.inputs = []
        self.outputs = []
        self.bargraphs = []
        self.displays = []
        
        def load_object(object_configuration, object_list):
            try:
                object_type = globals().get(configuration['type'])
                log.debug("Found type: " + configuration['type'])
            except AttributeError:
                log.warn("Type not found in '" + object_configuration + "'")
                return

            object_configuration.pop('type')
            if not object_configuration.get('options'):
                object_configuration['options'] = None
                log.debug("No options found, adding blank")

            log.debug(object_configuration)
            object_list.append(object_type(self.arduino, **object_configuration))

        # Open the configuration file
        with open(self.conf, 'r') as f:
            j = json.load(f)
        
        # Load the joysticks
        for joyIndex in j['joys']:
            if joyIndex['name'] == 'Joy0':
                self.joy0 = Joy(self.arduino, **joyIndex)
                log.info("Adding Joy0")
            elif joyIndex['name'] == 'Joy1':
                self.joy1 = Joy(self.arduino, **joyIndex)
                log.info("Adding Joy1")
            else:
                log.warn("Unknown joystick: " + joyIndex['name'])
        
        # Load all the objects!
        log.info("Loading objects from configuration")
        for key, value in {'inputs':       self.inputs,
                           'outputs':      self.outputs,
                           'bargraphs':    self.bargraphs,
                           'displays':     self.displays
                           }.iteritems():
            log.info("Loading objects from " + key)
            for configuration in j[key]:
                log.debug("Loading object '" + configuration['name'] + "'")
                load_object(configuration, value)
                log.debug("Object loaded successfully")

        f.close()
        
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
                log.debug("Connection state: " + str(state))
        # Otherwise just return True
        else:
            state = True
        
        return state

    def do(self):
        """Act based on the game state."""
        states = ["Online", "Paused", "Antenna is unpowered", "Antenna is off", "No antenna found", "No vessel"]

        if not self.headless and self.ready():
            state = None
            try:
                state = self.vessel.get("pause_state")
                state = int(state)
            except (ValueError, TypeError):
                if state is None:
                    state = 5
                else:
                    log.error("Unhandled state: " + str(state))
                    return

            if state > 5:
                log.error("Unhandled state: " + str(state))
                return

            log.debug("Telemachus state: " + str(state) + ": " + states[int(state)])
        else:
            state = 0

        if state == 0:
            self.online()
        else:
            while state == self.vessel.get("pause_state"):
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
                # If fly-by-wire is disabled, enable it
                if self.flybywire != 1:
                    self.flybywire = 1
                    log.info("Enabling fly-by-wire")
                    self.send_flybywire("toggle_fbw", "1")

                # Send fly-by-wire
                self.send_flybywire("six_dof", six_dof)
            else:
                # If fly-by-wire is enabled, disable it
                if self.flybywire != 0:
                    self.flybywire = 0
                    log.info("Disabling fly-by-wire")
                    self.send_flybywire("toggle_fbw", "0")
        
        # Iterate across devices
        for device in self.devices:
            if device.name in self.configuration['devices']:
                if issubclass(type(device), pin.__output):
                    device.set(self.get_telemetry(device.api))

                elif issubclass(type(device), pin.__input):
                    # Get the value from hardware
                    device.update()

                    # If it had changed
                    if device.changed():
                        # Send the update
                        self.send_flybywire(device.api, device.toString())
                else:
                    log.error("Unhandled type" + str(type(device)) + " for device " + device.name)

        # Iterate across displays
        for display in self.displays:
            if display.name in self.configuration['displays']:
                if issubclass(type(display), Bargraph):
                    display.set(self.get_telemetry(display.api), self.get_telemetry(display._max_api))

                elif issubclass(type(display), SevenSegment):
                    display.set(self.get_telemetry(display.api))

                else:
                    log.error("Unhandled type" + str(type(device)) + " for display " + device.name)


        for i in self.inputs:
            # Get the value from hardware
            i.update()

            # If it had changed
            if i.changed():
                # Send the update
                self.send_flybywire(i.api, i.toString())
            
        # Set the outputs
        for o in self.outputs:
            o.set(self.get_telemetry(o.api))
            
        # Set the bargraphs
        for b in self.bargraphs:
            b.set(self.get_telemetry(b.api), self.get_telemetry(b._max_api))
        
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
        
        log.debug(api + "=" + str(value))
        
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
        opts, args = getopt.getopt(argv, "hd:c:", ["help", "debug=", "config="])
    except getopt.GetoptError:
        usage()
        exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            exit()
        elif opt in ("-d", "--debug"):
            try:
                arg = int(arg)
                log.debug("Debug level received: " + str(arg))
            except ValueError:
                log.warn("Invalid log level: " + arg)
                continue

            if 0 <= arg <= 5:
                log.setLevel(60 - (arg*10))
                log.critical("Log level changed to: " + str(logging.getLevelName(60 - (arg*10))))
            else:
                log.warn("Invalid log level: " + str(arg))
        elif opt in ("-c", "--config"):
            filename = arg
    
    if filename is None:
        k = KAPCOM()
    else:
        k = KAPCOM(filename)

    log.info("Ready for input:")

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
    print "Cycles:        %s" % _cycles
    
    if _cycles > 0:
        print "Rate:          %.2fms" % (float(_duration)*1000)
        print "Frequency:     %.2fHz" % (1/float(_duration))


if __name__ == "__main__":    
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)