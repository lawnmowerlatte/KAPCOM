#!/usr/bin/python

pyksp_git="https://github.com/lawnmowerlatte/pyksp.git"

try:
    import sys
    import os
    import platform
    import time
    import datetime
    import socket
    import atexit
    import json
except ImportError:
    print("Failed to import necessary core modules.")
    exit()

debugger = 6
usecolor = False
tryinstall = False


def debug(message=None, level=debugger, newline=True, color=None):
    """Debugging log message"""
    
    if message is None:
        message = ""
    
    if color is not None and usecolor is True:
        message = termcolor.colored(message, color)
    
    if level <= debugger:
        if newline:
            print(message) 
        else:
            sys.stdout.write(message)


def ok():
    """Print OK message"""
    debug("OK", color="green")


def fail(message=None, end=True):
    """Print fail message"""
    debug("Fail", color="red")
    if message is not None:
        if end:
            debug()
            debug(message, color="red")
            exit()
        else:
            debug(message, newline=False)

# If termcolor is already installed, use it from the start
# We'll try to install it later if not...
if platform.system() != 'Windows':
    try:
        import termcolor
        usecolor = True
    except ImportError:
        pass

debug("Checking Python version: ", newline=False)
if "2.7" in sys.version.partition(' ')[0]:
    ok()
else:
    fail("Please use Python 2.7")

# Check for pip
debug("Checking for pip: ", newline=False)
try:
    import pip
    tryinstall = True
    ok()
except ImportError:
    fail(end=False)
    debug("Setup will continue, but will not be able to install packages automatically. Setup will fail if packages are missing.")
    
# Opportunistically use termcolor if available
if platform.system() != 'Windows':
    debug("Checking for termcolor: ", newline=False)
    try:
        import termcolor
        usecolor = True
        ok()
    except ImportError:
        fail(end=False)
        
        if tryinstall:
            debug("Installing termcolor: ", newline=False)
            try:
                pip.main(["install", "-q", "termcolor"])
                import termcolor
                ok()
            except ImportError:
                fail("Not required, continuing.", False)
        else:
            debug("Termcolor is not required, continuing.")
    
# Check for PySerial
debug("Checking for PySerial: ", newline=False)
try:
    import serial
    ok()
except ImportError:
    fail(end=False)
    
    if tryinstall:
        debug("Installing PySerial: ", newline=False)
        try:
            pip.main(["install", "-q", "pyserial"])
            import serial
            ok()
        except:
            fail("Installation failed, please install pyserial using pip.")
    else:
        fail("Please install pyserial using pip.")

# Check for serial toolchain
debug("Checking for serial tools: ", newline=False)
if platform.system() == 'Windows':
    try:
        import _winreg as winreg
        import itertools
        ok()
    except ImportError:
        fail(end=False)
        if tryinstall:
            debug("Installing winreg and itertools: ", newline=False)
            try:
                pip.main(["install", "-q", "winreg"])
                pip.main(["install", "-q", "itertools"])
                import _winreg as winreg
                import itertools
                ok()
            except:
                fail("Installation failed, please install winreg and itertools using pip.")
        else:
            fail("Please install winreg and itertools using pip.")

elif platform.system() == 'Darwin':
    try:
        from serial.tools import list_ports
        ok()
    except ImportError:
        fail("Not found, please install serial.tools using pip.")

else:
    try:
        import glob
        ok()
    except ImportError:
        fail(end=False)
        if tryinstall:
            debug("Installing glob: ", newline=False)
            try:
                pip.main(["install", "-q", "glob"])
                import glob
                ok()
            except:
                fail("Installation failed, please install glob using pip.")
        else:
            fail("Please install glob using pip.")

debug("Checking for PyAutoGUI", newline=False)
try:
    import pyautogui
    ok()
except ImportError:
    fail(end=False)
    if tryinstall:
        debug("Installing pyautogui: ", newline=False)
        try:
            pip.main(["install", "-q", "pyautogui"])
            import pyautogui
            ok()
        except:
            fail("Installation failed, please install pyautogui using pip.")
    else:
            fail("Please install pyautogui using pip.")

debug("Checking for pyksp: ", newline=False)

try:
    sys.path.append("./pyksp")
    import pyksp
    ok()
except ImportError:
    fail(end=False)
    if platform.system() != "Windows":
        debug("Trying to install pyksp: ", newline=False)
        try:
            if os.system("which git 2>&1 > /dev/null") == 0:
                if os.system("git clone -q " + pyksp_git + "  2>&1 > /dev/null") == 0:
                    sys.path.append("./pyksp")
                    import pyksp
                    ok()
                else:
                    fail("Clone failed.", False)
            else:
                fail("Couldn't find git", False)
        except:
            fail("Installation failed", False)
    else:
        debug("Please install pyksp within the KAPCOM directory using git", False)
        debug("git clone -q " + pyksp_git)
        exit()
    
debug()
debug("Prerequisites met. Please run configure.py", color="green")