#! /usr/bin/python

import os
import sys
import json
import getopt
import logging
from flask import Flask, request, render_template, redirect, url_for

sys.path.append(os.getcwd() + "/libraries")
from kapcom import KAPCOM
from bargraph import Bargraph
from sevensegment import SevenSegment

# Logging
_name = "KAPCOM Interface"
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

app = Flask("Flask App")
app.secret_key = 'TuKfzxdpLWpkBViZovZJCbWwfzHUveLyAtGVzdCJ3j9wrsLdHZ'
configuration = {
    "file": "kapcom.json",
    "data": json.load(open("config/kapcom.json", "r"))
}
k = None


@app.route("/configure")
def configure():
    return render_template('configure.html')


@app.route("/configure/file_<string:action>")
def configure_file_api(action):
    global configuration
    code = 200

    json_files = [f for f in os.listdir("./config") if '.json' in f]

    if request.method == 'GET':
        filename = request.args.get("file")
    elif request.method == 'POST':
        filename = request.form.get("file")
    else:
        filename = ""

    if filename == "":
        return "false", 405

    if filename is not None and not filename.endswith(".json"):
        filename += ".json"

    if action == "load":
        if filename is not None:
            configuration['file'] = filename

            with open(configuration['file'], 'r') as f:
                configuration['data'] = json.load(f)

            data = True
        else:
            data = False
            code = 405

    elif action == "save":
        with open(configuration['file'], 'w') as f:
            json.dump(configuration['data'], f, sort_keys=True, indent=4, separators=(',', ': '))
        data = True

    elif action == "save_as":
        if filename is not None and filename not in json_files:
            configuration['file'] = filename

            with open(configuration['file'], 'w') as f:
                json.dump(configuration['data'], f, sort_keys=True, indent=4, separators=(',', ': '))

            data = True
        else:
            data = False
            code = 405

    elif action == "new":
        if filename is not None and filename not in json_files:
            data = {
                "arduino": {},
                "configuration": {
                    "devices": [],
                    "displays": []
                },
                "modes": {
                    "default": {
                        "devices": "",
                        "displays": ""
                    },
                    "devices": {},
                    "displays": {}
                }
            }

            with open(filename, 'w') as f:
                json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

            data = True
        else:
            data = False
            code = 405

    elif action == "list":
        data = json_files

    elif action == "current":
        data = configuration['file']

    elif action == "delete":
        os.remove(filename)
        data = True

    else:
        data = False
        code = 405

    return json.dumps(data), code


@app.route("/configure/get_<string:action>")
def configure_get_api(action):
    global configuration
    code = 200

    if request.method == 'GET':
        name = request.args.get("name")
        object_type = request.args.get("type")
    elif request.method == 'POST':
        name = request.form.get("name")
        object_type = request.form.get("type")
    else:
        return "", 405

    if name is not None and name != "" and name != "null":
        if action == "arduino":
            data = configuration["data"]["arduino"][name]
        elif action == "device":
            data = [x for x in configuration["data"]["configuration"]["devices"] if x['name'] == name][0]
        elif action == "display":
            data = [x for x in configuration["data"]["configuration"]["displays"] if x['name'] == name][0]
        elif action == "device_mode":
            data = configuration["data"]["modes"]["devices"][name]
        elif action == "display_mode":
            data = configuration["data"]["modes"]["displays"][name]
        else:
            return "", 405

    elif object_type is not None and object_type != "" and object_type != "null":
        if action == "display":
            data = [x for x in configuration["data"]["configuration"]["displays"] if x['type'] == object_type]
        else:
            return "", 405

    else:
        if action == "general":
            data = {key: value for (key, value) in configuration["data"].iteritems()
                    if not isinstance(value, list) and not isinstance(value, dict)}
        elif action == "arduino":
            data = configuration["data"]["arduino"]
        elif action == "device":
            data = configuration["data"]["configuration"]["devices"]
        elif action == "display":
            data = configuration["data"]["configuration"]["displays"]
        elif action == "device_mode":
            data = configuration["data"]["modes"]["devices"]
        elif action == "display_mode":
            data = configuration["data"]["modes"]["displays"]
        elif action == "default_device_mode":
            data = configuration["data"]["modes"]["default"]["devices"]
        elif action == "default_display_mode":
            data = configuration["data"]["modes"]["default"]["displays"]
        else:
            return "", 405

    return json.dumps(data), code


@app.route("/configure/set_<string:action>")
def configure_set_api(action):
    global configuration
    data = ""
    code = 200

    if request.method != 'GET':
        return "", 405

    if action == "general":
        host = request.args.get("host")
        port = request.args.get("port")
        baud = request.args.get("baud")
        default_display_mode = request.args.get("default-display-mode")
        default_device_mode = request.args.get("default-device-mode")
        headless = request.args.get("headless")

        if host is not None and host != "":
            configuration['data']['host'] = host
        else:
            try:
                configuration['data'].pop('host')
            except KeyError:
                log.debug("Unable to find key 'host'")

        if port is not None and port != "":
            configuration['data']['port'] = port
        else:
            try:
                configuration['data'].pop('port')
            except KeyError:
                log.debug("Unable to find key 'port'")

        if baud is not None and baud != "":
            configuration['data']['baud'] = baud
        else:
            try:
                configuration['data'].pop('baud')
            except KeyError:
                log.debug("Unable to find key 'baud'")

        if headless == "on":
            configuration['data']['headless'] = True
        else:
            try:
                configuration['data'].pop('headless')
            except KeyError:
                log.debug("Unable to find key 'headless'")

        if default_display_mode is not None:
            configuration["data"]["modes"]["default"]["displays"] = default_display_mode
        else:
            configuration["data"]["modes"]["default"]["displays"] = ""

        if default_device_mode is not None:
            configuration["data"]["modes"]["default"]["devices"] = default_device_mode
        else:
            configuration["data"]["modes"]["default"]["devices"] = ""

        data = True

    elif action == "arduino":
        key = request.args.get("key")
        name = request.args.get("name")
        uuid = request.args.get("uuid")
        bargraphs = request.args.get("bargraphs")
        sevensegments = request.args.get("sevensegments")
        default = request.args.get("default")

        if key not in configuration['data']['arduino']:
            return False, 500

        if name != key:
            configuration['data']['arduino'][name] = configuration['data']['arduino'].pop(key)

        if uuid is not None:
            configuration['data']['arduino'][name]['uuid'] = uuid
        else:
            try:
                configuration['data']['arduino'][name].pop('uuid')
            except KeyError:
                log.debug("Unable to find key 'uuid'")

        if bargraphs is not None:
            configuration['data']['arduino'][name]['bargraphs'] = bargraphs
        else:
            try:
                configuration['data']['arduino'][name].pop('bargraphs')
            except KeyError:
                log.debug("Unable to find key 'bargraphs'")

        if sevensegments is not None:
            configuration['data']['arduino'][name]['sevensegments'] = sevensegments
        else:
            try:
                configuration['data']['arduino'][name].pop('sevensegments')
            except KeyError:
                log.debug("Unable to find key 'sevensegments'")

        if default != "on":
            try:
                configuration['data']['arduino'][name].pop('default')
            except KeyError:
                log.debug("Unable to find key 'default'")
        else:
            configuration['data']['arduino'][name]['default'] = True

    elif action == "display":
        key = request.args.get("key")
        name = request.args.get("name")
        object_type = request.args.get("type")
        api = request.args.get("api")
        max_api = request.args.get("max_api")
        max_value = request.args.get("max_value")

        if key not in [value['name'] for value in configuration['data']['configuration']['displays']]:
            return "false", 500

        display = [value for value in configuration['data']['configuration']['displays'] if value['name'] == key][0]

        if name != key and name is not None and name != "":
            display['name'] = name

        if object_type is not None:
            display['type'] = object_type

        if api is not None:
            display['api'] = api

        if object_type == "Bargraph":
            if max_api is not None:
                try:
                    display['options'].pop('max_value')
                except KeyError:
                    log.debug("Unable to find key 'max_value'")
                display['options']['max_api'] = max_api
            elif max_value is not None:
                try:
                    display['options'].pop('max_api')
                except KeyError:
                    log.debug("Unable to find key 'max_api'")
                display['options']['max_value'] = max_value
        else:
            try:
                display['options'].pop('max_api')
            except KeyError:
                log.debug("Unable to find key 'max_api'")

            try:
                display['options'].pop('max_value')
            except KeyError:
                log.debug("Unable to find key 'max_value'")

    elif action == "device":
        key = request.args.get("key")
        name = request.args.get("name")
        object_type = request.args.get("type")
        api = request.args.get("api")
        pin = request.args.get("pin")
        x = request.args.get("x")
        y = request.args.get("y")
        z = request.args.get("z")
        button = request.args.get("button")
        modifier = request.args.get("modifier")
        indicator = request.args.get("indicator")

        if key not in [value['name'] for value in configuration['data']['configuration']['devices']]:
            return "false", 500

        device = [value for value in configuration['data']['configuration']['devices'] if value['name'] == key][0]

        if name != key and name is not None and name != "":
            device['name'] = name

        if object_type is not None:
            device['type'] = object_type

        if api is not None:
            device['api'] = api

        for x in ["x", "y", "z", "modifier", "indicator", "button", "pin"]:
            try:
                device.pop(x)
            except KeyError:
                log.debug("Unable to find key '" + x + "'")

        if object_type == "Joy":
            device['x'] = x
            device['y'] = y
            device['z'] = z
            device['button'] = button
        elif object_type == "Mod":
            device['modifier'] = modifier
            device['indicator'] = indicator
            device['button'] = button
        else:
            device['pin'] = pin

    elif action == "device_mode":
        name = request.args.get("name")

        if name is None or name == "":
            return "false", 500

        configuration['data']['modes']['devices'][name] = request.args.getlist("device")

    elif action == "display_mode":

        name = request.args.get("name")
        arduino = request.args.get("arduino")

        if name is None or name == "":
            return "false", 500

        if arduino is None or arduino == "":
            return "false", 500

        sevensegment_count = configuration['data']['arduino'][arduino]['sevensegments']
        bargraph_count = configuration['data']['arduino'][arduino]['bargraphs']

        sevensegments = []
        bargraphs = []

        for i in range(int(sevensegment_count)):
            sevensegments.append(request.args.get("display-sevensegment-" + str(i)))

        for i in range(int(bargraph_count)):
            bargraphs.append(request.args.get("display-bargraph-" + str(i)))

        configuration['data']['modes']['displays'][name]['SevenSegment'][arduino] = sevensegments
        configuration['data']['modes']['displays'][name]['Bargraph'][arduino] = bargraphs

        data = True

    return json.dumps(data), code


@app.route("/configure/delete_<string:action>")
def configure_delete_api(action):
    global configuration
    code = 200

    if request.method == 'GET':
        name = request.args.get("name")
    elif request.method == 'POST':
        name = request.form.get("name")
    else:
        return False, 405

    if name is not None and name != "" and name != "null":
        if action == "arduino":
            data = configuration["data"]["arduino"].pop(name)
        elif action == "device":
            data = [x for x in configuration["data"]["configuration"]["devices"] if x['name'] != name]
            configuration["data"]["configuration"]["devices"] = data
        elif action == "display":
            data = [x for x in configuration["data"]["configuration"]["displays"] if x['name'] != name]
            configuration["data"]["configuration"]["displays"] = data
        elif action == "device_mode":
            data = configuration["data"]["modes"]["devices"].pop(name)
        elif action == "display_mode":
            data = configuration["data"]["modes"]["displays"].pop(name)
        else:
            return False, 405

    else:
        return False, 405

    return json.dumps(data), code


@app.route("/configure/new_<string:action>")
def configure_new_api(action):
    global configuration
    code = 200

    if request.method == 'GET':
        name = request.args.get("name")
    elif request.method == 'POST':
        name = request.form.get("name")
    else:
        return "", 405

    if name is not None and name != "" and name != "null":
        if action == "arduino":
            if name not in configuration["data"]["arduino"]:
                configuration["data"]["arduino"][name] = {}
                data = True
            else:
                data = False
                code = 409
        elif action == "device":
            if name not in configuration["data"]["configuration"]["devices"]:
                configuration["data"]["configuration"]["devices"].append({"name": name})
                data = True
            else:
                data = False
                code = 409
        elif action == "display":
            if name not in configuration["data"]["configuration"]["displays"]:
                configuration["data"]["configuration"]["displays"].append({"name": name})
                data = True
            else:
                data = False
                code = 409
        elif action == "device_mode":
            if name not in configuration["data"]["modes"]["devices"]:
                configuration["data"]["modes"]["devices"][name] = {}
                data = True
            else:
                data = False
                code = 409
        elif action == "display_mode":
            if name not in configuration["data"]["modes"]["displays"]:
                configuration["data"]["modes"]["displays"][name] = {}
                data = True
            else:
                data = False
                code = 409
        else:
            return "", 405

    else:
        return False, 405

    return json.dumps(data), code


@app.route("/api/<string:action>", methods=['GET', 'POST'])
def api(action):
    global k
    page = ""
    code = 200

    if action == "status":
        page = json.dumps(k.running)
    elif action == "stop":
        k.stop()
        page = "Stopping"
    elif action == "start":
        k.start()
        page = "Starting"
    elif action == "restart":
        k.restart()
        page = "Restarting"

    elif action == "reconfigure":
        if request.method == 'GET':
            filename = request.args["filename"]
        else:
            return "", 405

        k.stop()
        k = KAPCOM(filename)

    elif action == "stats":
        json_files = k.stats()
        page = json.dumps(json_files)

    elif action == "get_available_files":
        json_files = [f for f in os.listdir("./config") if '.json' in f]
        page = json.dumps(json_files)

    elif action == "get_current_file":
        json_files = k.filename
        page = json.dumps(json_files)

    elif action == "get_current_mode":
        if request.method == 'GET':
            mode_type = request.args["type"]
        else:
            return "", 405
        data = k.get_current_mode(mode_type)
        page = json.dumps(data)

    elif action == "get_available_modes":
        if request.method == 'GET':
            mode_type = request.args["type"]
        else:
            return "", 405

        data = k.get_available_modes(mode_type)
        page = json.dumps(data)

    elif action == "set_mode":
        if request.method == 'GET':
            mode_type = request.args["type"]
            mode = request.args["mode"]
        else:
            return "", 405

        data = k.set_mode(mode_type, mode)
        page = json.dumps(data)

    elif action == "get_current_display":
        if request.method == "GET":
            arduino = request.args.get("arduino")
            display_type = request.args.get("type")
            try:
                index = int(request.args.get("index"))
            except KeyError:
                index = None
        else:
            return "", 405

        data = k.get_current_display(arduino, display_type, index)
        page = json.dumps(data)

    elif action == "get_available_displays":
        if request.method == "GET":
            display_type = request.args.get("type")
        else:
            return "", 405

        data = k.get_available_displays(display_type)
        page = json.dumps(data)

    elif action == "set_display":
        if request.method == "GET":
            new_name = request.args["name"]
            arduino = request.args["arduino"]
            display_type = request.args["type"]
            index = int(request.args["index"])
        elif request.method == "POST":
            new_name = request.form["name"]
            arduino = request.form["arduino"]
            display_type = request.form["type"]
            index = int(request.form["index"])
            code = 302
        else:
            return "", 405

        data = k.set_display(new_name, arduino, display_type, index)
        page = json.dumps(data)

    elif action == "get_display":
        if request.method == "GET":
            name = request.args["name"]
        else:
            return "", 405

        data = k.get_display(name)
        page = json.dumps(data)

    elif action == "get_available_formats":
        if request.args["type"] == "SevenSegment":
            page = json.dumps(SevenSegment.formats)

        elif request.args["type"] == "Bargraph":
            page = json.dumps(Bargraph.formats)
        else:
            code = 400

    elif action == "set_format":
        if request.method == "GET":
            name = request.args["name"]
            new_format = request.args["format"]
        else:
            return "", 400

        display = k.displays.get(name)

        display._type = new_format

        # page = json.dumps(display)

    else:
        page = '{"Error": "Unimplemented API"}'
        code = 501

    if code == 302:
        return redirect(url_for('run'))

    return page, code


@app.route("/")
def run():
    return render_template('layout.html')


def usage():
    """Print out a usage message"""

    print "%s [-h] [-d level|--debug level] [-c file|--config file]" % sys.argv[0]


def main(argv):
    """Create KAPCOM object, initialize and run."""
    global k
    filename = None

    opts, args = None, None
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

    k = KAPCOM(filename)

    app.debug = True

    app.run()


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    # except:
    #     sys.exit(0)