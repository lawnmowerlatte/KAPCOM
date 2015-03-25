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
from arduino import arduino

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
        
        # Iterate over lists to sync hardware and software
        # Do the interesting stuff here
        
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