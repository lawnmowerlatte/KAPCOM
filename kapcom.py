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
from pin import *
from mod import Mod
from joy import Joy
from bargraph import Bargraph
from sevensegment import SevenSegment

_cycles = 0
_duration = 0

# Logging
_name = "KAPCOM"
_debug = logging.INFO
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
        "vessel_orbital_velocity",
        "vessel_surface_velocity",
        "vessel_atmospheric_density",
        "vessel_surface_speed",
        "vessel_gee_force",
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
        "resource_ia_current",
        "resource_ia_max",
        "resource_xg_current",
        "resource_xg_max",
        
        "sas_status",
        "rcs_status",
        "action_group_light",
        "action_group_gear",
        "action_group_brake"
    }

    # Set default values
    defaults = {
        'file':     "kapcom.json",
        'baud':     115200,
        'host':     "127.0.0.1",
        'port':     8085,
        'headless': False
    }

    def __init__(self, file=None, baud=None, host=None, port=None, headless=False):
        """
        Creates the KAPCOM object
        Reads the configuration file and sets attributes
        Runs initialization until successful
        :param file: Configuration file
        :param baud: Bitrate for Arduino devices
        :param host: Telemachus host
        :param port: Telemachus port
        :param headless: True if we are using fake telemetry data
        :return: KAPCOM object
        """

        # Define configuration options as blanks
        self.file = None
        self.baud = None
        self.host = None
        self.port = None
        self.headless = None

        # Define empty lists for objects
        self.configuration = None
        self.arduino = {}
        self.devices = {}
        self.displays = {}
        self.mode = {
            "displays": "default",
            "devices": "default"
        }

        # Set initial value of Fly-by-wire to off
        self.flybywire = False

        def set_configuration(parameter_name, argument, configuration, default):
            """Loads the object parameter, taking into account arguments, the configuration file and defaults"""

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
        set_configuration("file", file, None, self.defaults.get("file"))

        # Open the file and load the JSON data
        with open(self.file, 'r') as config_file:
            self.configuration = json.load(config_file)

            # For the list of default values
            for parameter, default_value in self.defaults.iteritems():
                # Get the argument
                argument_value = eval(parameter)
                # Get the configuration
                configuration_value = self.configuration.get(parameter)
                # Set object value
                set_configuration(parameter, argument_value, configuration_value, default_value)

        # Close the configuration file
        config_file.close()

        # If we are not headless, connect to Telemachus via PyKSP
        if not self.headless:
            # Connect
            self.vessel = pyksp.ActiveVessel(url=self.host + ":" + str(self.port))
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
        """
        Attempt to connect to Arduino. Configure all devices. Preload devices. Attempt to connecto Telemachus.
        :return: True if successful, False if failed
        """
        # Connect to Arduino
        log.info("Initializing fly-by-wire system")
        self.arduino = {}
        for key, details in self.configuration['arduino'].iteritems():
            log.debug("Initializing Arduino: " + key)
            self.arduino[key] = Arduino(details.get('uuid'), details.get('port'), details.get('baud') or self.baud)

            if details.get('default') is True:
                setattr(self.arduino[key], "default", True)
            else:
                setattr(self.arduino[key], "default", False)

        defaults = len([val for (key, val) in self.arduino.iteritems() if val.default is True])
        total = len(self.arduino)

        if total == 0:
            log.critical("No Arduino devices defined in configuration file.")
            exit()

        if defaults > 1:
            log.warn("Multiple defaults set, clearing all")
            for key, a in self.arduino.iteritems():
                setattr(a, "default", False)
            defaults = len([val for (key, val) in self.arduino.iteritems() if val.default is True])

        if defaults == 0:
            log.warn("No default set, using first device:")
            for key, a in self.arduino.iteritems():
                log.warn("Selecting Arduino '" + key + "' as default")
                setattr(a, "default", True)
                break
        log.info("Fly-by-wire initialized")

        # Configure
        log.info("Reading configuration and creating objects")
        try:
            self.configure()
        except IOError:
            log.error("Failed t o read configuration file.")
            return False
        log.info("Configuration successful")

        # If we're not headless, connect
        if not self.headless:
            log.info("Connecting to ship telemetry")

            # Connect to the Telemachus socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.port))

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
        """
        Read the configuration file and create objects
        :return: None
        """

        # Clear any previous configuration
        self.devices = {}
        self.displays = {}

        def create_object(object_configuration):
            try:
                object_type = globals().get(configuration['type'])
                log.debug("Found type: " + configuration['type'])
                object_configuration.pop('type')
            except AttributeError:
                log.warn("Type not found in '" + object_configuration + "'")
                return

            if not object_configuration.get('options'):
                object_configuration['options'] = None
                log.debug("No options found, adding blank")

            try:
                arduino_id = configuration.pop('arduino')
            except KeyError:
                log.warn("No Arduino specified, using default.")
                arduino_id = [key for (key, val) in self.arduino.iteritems() if val.default is True][0]

            log.debug(object_configuration)

            if object_type == SevenSegment or object_type == Bargraph:
                return object_type(**object_configuration)
            else:
                return object_type(self.arduino[arduino_id], **object_configuration)


        # Load all the objects!
        log.info("Loading objects from configuration")
        for key, device_list in {'devices':       self.devices,
                                 'displays':      self.displays
                                 }.iteritems():
            log.info("Loading objects from " + key)
            for configuration in self.configuration['configuration'][key]:
                log.debug("Loading object '" + configuration['name'] + "'")
                device_list[configuration['name']] = create_object(configuration.copy())
                log.debug("Object loaded successfully")

        self.change_mode('displays', self.configuration['modes']['default']['displays'])
        self.change_mode('devices', self.configuration['modes']['default']['devices'])


    def change_mode(self, mode_type, mode):
        """
        Change the KAPCOM configuration based on a named configuration set.
        :param mode_type: Type of configuration to change: Device or Display
        :param mode: Named mode from configuration file
        :return:
        """

        if mode == "default":
            log.info("Setting default mode for " + mode_type)
            self.change_mode(mode_type, self.configuration['modes']['default'][mode_type])
            return

        self.mode[mode_type] = mode
        log.info("Setting mode " + mode + " for type" + mode_type)

        if mode_type == "displays":
            log.debug("Detatching all displays")

            # Loop over displays
            for display_name, display in self.displays.iteritems():
                log.debug("Detatching display " + display_name)

                # Detatch the display
                display.detatch()

                log.debug("Checking for reattachment")
                # Loop over Arduinos
                for arduino_name, arduino in self.arduino.iteritems():
                    log.debug("Checking " + arduino_name)

                    try:
                        # If the display is present in the Arduino configuration
                        index = self.configuration['modes']['displays'][self.mode['displays']][display.__class__.__name__].get(arduino_name)\
                            .index(display.name)
                        # Attach the display
                        display.attach(arduino, index)
                        log.info("Attached display " + display_name + " to Arduino " + arduino_name)
                        break
                    except (ValueError, AttributeError):
                        log.debug("Did not find display " + display.name + " for Arduino " + arduino_name)


    def ready(self):
        """Attempt to connect to Telemachus."""
        
        state = False

        # If we're not headless, check the socket
        if not self.headless:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            r = s.connect_ex((self.host, self.port))
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
        # Get list of joysticks currently configured
        joys = {key: value for (key, value) in self.devices.iteritems() if type(value) is Joy \
                and value.name in self.configuration['modes']['devices'][self.mode['devices']]}

        # Update all configured joysticks
        for joy in joys:
            log.debug("Updating Joystick: " + joy)
            self.devices[joy].update()

        # Get list of centered joysticks
        joys_active = {key: value for (key, value) in joys.iteritems() if value.centered is False}
        log.debug("Found " + str(len(joys)) + " in current mode, " + str(len(joys_active)) + " are active")

        # If any joysticks are active
        if len(joys_active) > 0:
            # If fly-by-wire is disabled, enable it
            if self.flybywire is False:
                self.flybywire = True
                log.info("Enabling fly-by-wire")
                self.send_flybywire("toggle_fbw", "1")

            # Send all active joysticks
            for name, joy in joys_active.iteritems():
                self.send_flybywire(joy.api, joy.toString())
        else:
            # If fly-by-wire is enabled, disable it
            if self.flybywire is True:
                self.flybywire = False
                log.info("Disabling fly-by-wire")
                self.send_flybywire("toggle_fbw", "0")

        # Iterate across devices
        for (device_name, device) in {key: value for (key, value) in self.devices.iteritems() \
                                      if type(value) is not Joy}.iteritems():
            if device.name in self.configuration['modes']['devices'][self.mode['devices']]:
                if type(device) == DigitalOut or type(device) == AnalogOut:
                    device.set(self.get_telemetry(device.api))

                elif type(device) == DigitalIn or type(device) == AnalogIn or type(device) == Mod:
                    # Get the value from hardware
                    device.update()

                    # If it had changed
                    if device.changed():
                        # Send the update
                        self.send_flybywire(device.api, device.toString())

                else:
                    log.error("Unhandled type: " + str(type(device)) + " for device " + device.name)

        # Iterate across displays
        for display_name, display in self.displays.iteritems():
            if display._arduino is not None:
                if type(display) == Bargraph:
                    display.set(self.get_telemetry(display.api), self.get_telemetry(display._max_api))

                elif type(display) == SevenSegment:
                    display.set(self.get_telemetry(display.api))

                else:
                    log.error("Unhandled type" + str(type(device)) + " for display " + device.name)

        
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