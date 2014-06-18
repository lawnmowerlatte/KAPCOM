
# This module allows programs to interface with Kerbal Space Program
# using the Telemachus websocket API.

# For the purposes of this module, input correlates to user input to be
# sent to the Telemachus API and output refers to vessel data provided
# by Kerbal Space Program to the Telemachus API.

# Input and output commands are run in separate persistent websocket 
# connections. All input data is sent on demand as it is generated. 
# All output data is data is refreshed every 250ms using a websocket
# subscription. This data can be polled at any time and the latest data
# will be used.

import websocket
import json
import time
import os
import math

class telemachus:
    """Creates an API instance for interacting with the Telemachus WebSocket API."""
    endpoint = ""
    interval = ""
    
    ws = {
        "input":    None,
        "output":   None 
    }

    api = {
        "input": [
            "f.sas",
            "f.rcs"            
        ],
        "output" : [
            "v.altitude",
            "f.throttle",
            "v.sasValue",
            "v.rcsValue"
        ]
    }
    
    def __init__(self, endpoint="ws://127.0.0.1/datalink", interval="250"):
        """Takes an endpoint address and interval and creates a Telemachus object."""
        
        # Set variables for future reference
        self.endpoint = endpoint
        self.interval = interval
        
        # Create WebSocket connection for intput INTO KSP
        self.ws['input'] = create_connection(self.endpoint)
        
        # Create WebSocket listener for updates FROM KSP
        self.ws['output'] = websocket.WebSocketApp(self.endpoint, 
                                on_message = ws_update, 
                                on_error = ws_error, 
                                on_close = ws_close)
        self.ws['output'].on_open = ws_subscribe
    
    def ws_error(ws):
        """Display errors on WebSocket connections."""
        print "WebSocket Error: %s" % error
    
    def ws_close(ws):
        """Display errors on WebSocket connection closures."""
        print "WebSocket connection closed."
        # Re-establish connection?
    
    def ws_subscribe():
        """Set up subscription to WebSocket API."""
        subscribe = """
{
"rate": %s,
"+": [ %s ]
}""" % (self.interval, ", ".join(api['output']))
        
        self.ws['output'].send("subscribe")
    
    def ws_update():
        """Update the object by parsing an incoming message from the Output WebSocket."""
        pass
        # To do
    
    def ws_post():
        """Send a command for all Input values in the object"""
        pass
        # To do
    
    def get(key):
        """Return the desired value from the Telemachus object."""
        return self.api[key]
    
    def set(key, value):
        """Set the value for the given key."""
        pass
        # To do
    
    def push():
        """Force the object to update the WebSocket connection for input"""
        pass
        # To do
    
    
    
        





### To do
# Incorporate special handling below

def read_facing(dimension):
    if dimension in ['pitch']:
        fresh_json = json.load(urllib2.urlopen(url + 'n.pitch'))
        result = math.radians(int(fresh_json["alt"]))
    elif dimension in ['yaw']:
        fresh_json = json.load(urllib2.urlopen(url + 'n.heading'))
        result = math.radians(int(fresh_json["alt"]))
    elif dimension in ['roll']:
        fresh_json = json.load(urllib2.urlopen(url + 'n.roll'))
        result = math.radians(int(fresh_json["alt"]))
    else:
        result = -1
    return result


def read_heading():
    #Note: This returns facing:yaw, not your heading over land
    #Basically what the navball shows, not 'true' heading
    fresh_json = json.load(urllib2.urlopen(url + 'n.heading'))
    result = math.radians(int(fresh_json["alt"]))
    return result


def read_inclination():
    fresh_json = json.load(urllib2.urlopen(url + 'o.inclination'))
    result = math.radians(int(fresh_json["alt"]))
    return result




