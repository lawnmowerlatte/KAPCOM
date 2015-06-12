#!/usr/bin/python

pyksp_git = "https://github.com/lawnmowerlatte/pyksp.git"

try:
    import sys
    import os
    import platform
    import time
    import datetime
    import socket
    import atexit
    import json
    import logging
except ImportError:
    print("Failed to import necessary core modules.")
    exit()

from tools import KAPCOMLog

_log = KAPCOMLog("Setup", logging.INFO)
log = _log.log

tryinstall = False

log.info("Checking Python version")
if "2.7" in sys.version.partition(' ')[0]:
    log.info("OK")
else:
    log.critical("Failed")
    log.critical("Please use Python 2.7")
    exit(1)

# Check for pip
log.info("Checking for pip")
try:
    import pip
    tryinstall = True
    log.info("OK")
except ImportError:
    log.error("Failed.")
    log.error("Setup will continue, but will not be able to install packages automatically. Setup will fail if packages are missing.")

# Check for PySerial
log.info("Checking for PySerial")
try:
    import serial
    log.info("OK")
except ImportError:
    log.warn("Failed")
    
    if tryinstall:
        log.info("Installing PySerial")
        try:
            pip.main(["install", "-q", "pyserial"])
            import serial
            log.info("Success")
        except ImportError:
            log.critical("Failed")
            log.critical("Installation failed, please install pyserial using pip.")
            exit(1)
    else:
        log.critical("Failed")
        log.critical("Please install pyserial using pip.")
        exit(1)
        
log.info("Checking for Flask")
try:
    import flask
    log.info("OK")
except ImportError:
    log.warn("Failed")

    if tryinstall:
        log.info("Installing Flask")
        try:
            pip.main(["install", "-q", "flask"])
            import flask
            log.info("OK")
        except ImportError:
            log.critical("Failed")
            log.critical("Installation failed, please install flask using pip.")
            exit(1)
    else:
        log.critical("Failed")
        log.critical("Please install flask using pip.")
        exit(1)

log.info("Checking for PyAutoGUI")
try:
    import pyautogui
    log.info("OK")
except ImportError:
    log.warn("Failed")

    if tryinstall:
        log.info("Installing pyautogui")
        try:
            pip.main(["install", "-q", "pyautogui"])
            import pyautogui
            log.info("OK")
        except ImportError:
            log.critical("Failed")
            log.critical("Installation failed, please install pyautogui using pip.")
            exit(1)
    else:
        log.critical("Failed")
        log.critical("Please install pyautogui using pip.")
        exit(1)

log.info("Checking for pyksp")
try:
    sys.path.append("./pyksp")
    import pyksp
    log.info("OK")
except ImportError:
    if platform.system() != "Windows":
        log.warn("Failed")

        log.info("Trying to install pyksp")
        try:
            if os.system("which git 2>&1 > /dev/null") == 0:
                if os.system("git clone -q " + pyksp_git + "  2>&1 > /dev/null") == 0:
                    sys.path.append("./pyksp")
                    import pyksp
                    log.info("OK")
                else:
                    log.critical("Fail")
                    log.critical("Clone failed")
                    exit(1)
            else:
                log.critical("Fail")
                log.critical("Couldn't find git binary")
                exit(1)
        except ImportError:
            log.critical("Fail")
            log.critical("Installation failed, please install pyksp from GitHub manually.")
            log.info("git clone -q " + pyksp_git)
            exit(1)
    else:
        log.critical("Fail")
        log.critical("Installation failed, please install pyksp from GitHub manually.")
        log.info("git clone -q " + pyksp_git)
        exit(1)
    
print()
log.info("Prerequisites met. Please run KAPCOM.py")