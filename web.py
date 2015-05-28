#! /usr/bin/python

import os
import sys
import json
import getopt
import logging
from flask import Flask, request, render_template, redirect, url_for
from kapcom import KAPCOM
from bargraph import Bargraph
from sevensegment import SevenSegment

# Logging
_name = "KAPCOM Web"
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
    "data": json.load(open("kapcom.json", "r"))
}
k = None

@app.route("/configure")
def configure():
    return render_template('configure.html')


@app.route("/configure/file_<string:action>")
def configure_file_api(action):
    global configuration
    data = ""
    code = 200

    json_files = [f for f in os.listdir("./") if '.json' in f]

    if request.method == 'GET':
        file = request.args.get("file")
    elif request.method == 'POST':
        file = request.form.get("file")

    if file == "":
        return "false", 405

    if file is not None and not file.endswith(".json"):
        file += ".json"

    if action == "load":
        if file is not None:
            configuration['file'] = file

            with open(configuration['file'], 'r') as f:
                configuration['data'] = json.load(f)

            data = True
        else:
            data = False
            code = 405

    elif action == "save":
        with open(configuration['file'], 'w') as f:
            json.dump(configuration['data'], f)
        data = True

    elif action == "save_as":
        if file is not None and file not in json_files:
            configuration['file'] = file

            with open(configuration['file'], 'w') as f:
                json.dump(configuration['data'], f)

            data = True
        else:
            data = False
            code = 405

    elif action == "new":
        if file is not None and file not in json_files:
            configuration['file'] = file
            configuration['data'] = {}

            with open(configuration['file'], 'w') as f:
                json.dump(configuration['data'], f)

            data = True
        else:
            data = False
            code = 405

    elif action == "list":
        data = json_files

    elif action == "current":
        data = configuration['file']

    elif action == "delete":
        os.remove(file)
        data = True

    else:
        data = False
        code = 405

    return json.dumps(data), code


@app.route("/configure/get_<string:action>")
def configure_get_api(action):
    global configuration
    data = ""
    code = 200

    if request.method == 'GET':
        name = request.args.get("name")
    elif request.method == 'POST':
        name = request.form.get("name")
    else:
        return "", 405

    if name is not None:
        if action == "arduino":
            data = configuration["data"]["arduino"][name]
        elif action == "device":
            data = configuration["data"]["configuration"]["devices"][name]
        elif action == "display":
            data = configuration["data"]["configuration"]["displays"][name]
        elif action == "device-mode":
            data = configuration["data"]["modes"]["devices"][name]
        elif action == "display-mode":
            data = configuration["data"]["modes"]["displays"][name]
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
        elif action == "device-mode":
            data = configuration["data"]["modes"]["devices"]
        elif action == "display-mode":
            data = configuration["data"]["modes"]["displays"]
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
        headless = request.args.get("headless")

        if host is not None:
            configuration['data']['host'] = host
        else:
            try:
                configuration['data'].pop('host')
            except:
                pass

        if port is not None:
            configuration['data']['port'] = port
        else:
            try:
                configuration['data'].pop('port')
            except:
                pass

        if baud is not None:
            configuration['data']['baud'] = baud
        else:
            try:
                configuration['data'].pop('baud')
            except:
                pass

        if headless != "on":
            try:
                configuration['data'].pop('headless')
            except:
                pass
        else:
            log.critical("Enabling headless mode")
            configuration['data']['headless'] = True

        data = True

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
        json_files = [f for f in os.listdir("./") if '.json' in f]
        page = json.dumps(json_files)

    elif action == "get_current_file":
        json_files = k.filename;
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
            except:
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

        display = k.displays.get(name)\

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
    global k, a
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