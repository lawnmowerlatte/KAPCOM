#!/usr/bin/python

pyksp_git="https://github.com/602p/pyksp.git"

try:
    import sys
    import os
    import platform
    import serial
    import time
    import datetime
    import socket
    import atexit
    import json
except:
    print("Failed to import necessary core modules.")
    exit()

debugger = 6
usecolor = False
def debug(message=None, level=debugger, newline=True, color=None):
    """Debugging log message"""
    
    if message is None:
        message=""
    
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

debug("Checking Python version: ", newline=False)
if ("2.7" in sys.version.partition(' ')[0]):
    ok()
else:
    fail("Please install Python 2.7")

debug("Checking for pip: ", newline=False)
if os.system("which pip 2>&1 > /dev/null") == 0:
    ok()
else:
    fail("Please install pip")
    
debug("Importing pip: ", newline=False)
try:
    import pip
except:
    fail("Unable to import pip for installation")
else:
    ok()
    
debug("Checking for termcolor: ", newline=False)
try:
    import termcolor
    usecolor = True
except:
    try:
        fail("Installing termcolor: ", False)
        pip.main('install', 'termcolor')
    except:
        fail("Not required, continuing.", False)
        debug()
    else:
        ok()
else:
    ok()
    
debug("Checking for serial tools: ", newline=False)
if platform.system() == 'Windows':
    try:
        import _winreg as winreg
        import itertools
    except:
        fail("Please install winreg and itertools")
    else:
        ok()
elif platform.system() == 'Darwin':
    try:
        from serial.tools import list_ports
    except:
        fail("Please install serial.tools")
    else:
        ok()
else:
    try:
        import glob
    except:
        fail("Please install glob")
    else:
        ok()
        
debug("Checking for pyksp: ", newline=False)
try:
    sys.path.append("./pyksp")
    import pyksp
except:
    if platform.system() is not "Windows":
        fail("Trying to install pyksp: ", False)
        try:
            if os.system("which git 2>&1 > /dev/null") == 0:
                if os.system("git clone -q " + pyksp_git + "  2>&1 > /dev/null") == 0:
                    sys.path.append("./pyksp")
                    import pyksp
            else:
                fail("Couldn't find git")
        except:
            fail("Please install pyksp within the KAPCOM directory")
        else:
            ok()
    else:
        fail("Please install pyksp within the KAPCOM directory")
else:
    ok()
    
debug()
debug("Prerequisites met. Please run configure.py", color="green")
    