function send_api(command, postdata) {
    console.log("Request: " + command + " : " + postdata);

    request = {
        async: false,
        url: "configure/" + command,
        dataType: 'json'
    }

    if (postdata != null) {
        request.data = postdata;
    }


    response = $.ajax(request);
    console.log("Response: " + response.responseJSON);

    return response.responseJSON;
}

function build_select(data, current, size, id, name, classes) {
    if (size == null) {
        size = ""
    } else {
        size = "size=" + size;
    }

    s = "<select " + size + " id='" + id + "' name='" + name + "' class='" + classes + "'>";

    for (item of data) {
        if (item == current) {
            s += "<option value='" + item + "' selected>" + item + "</option>";
        } else {
            s += "<option value='" + item + "'>" + item + "</option>";
        }

    }

    s += "</select>";
    return s;
}

function build_pin_list(id, name, css, current) {
    s = "<select  id='" + id +"' name='" + name + "' class='" + css + "'>";
    s += "<optgroup label='Digital'>";

    for (var i = 0; i<54; i++) {
        if (i == current) {
            s += "<option value='" + i + "' selected>" + i + "</option>";
        } else {
            s += "<option value='" + i + "'>" + i + "</option>";
        }
    }

    s += "</optgroup>";

    current -= 160;

    s += "<optgroup label='Analog'>";

    for (var i = 0; i<16; i++) {
        if (i == current) {
            s += "<option value='A" + (160+i) + "' selected>" + i + "</option>";
        } else {
            s += "<option value='" + (160+i) + "'>" + i + "</option>";
        }
    }

    s += "</optgroup>";
    s += "</select>";


    return s;
}

function refresh_file_selector() {
    data = send_api("file_list");
    current = send_api("file_current");

    s = build_select(data, current, 5, "File-List", "file", "list")

    s += "<input id='File-New' class='list-button' type='submit' value='New' />";
    s += "<input id='File-Load' class='list-button' type='submit' value='Load' />";
    s += "<input id='File-Save' class='list-button' type='submit' value='Save' />";
    s += "<input id='File-Save-As' class='list-button' type='submit' value='Save As' />";
    s += "<input id='File-Delete' class='list-button' type='submit' value='Delete' />";

    console.log(s);
    $("#File-Selector").html(s);


    $("#File-New").click(function() {
        var name = prompt("New filename:");

        console.log("Creating: " + name);
        data = send_api("file_new", "file=" + name);

        refresh_file_selector();
    });

    $("#File-Load").click(function() {
        var name = $("#File-List").val();

        console.log("Loading: " + name);
        data = send_api("file_load", "file=" + name);

        refresh_all();
    });

    $("#File-Save").click(function() {
        console.log("Saving as current file.");
        data = send_api("file_save");

        refresh_file_selector();
    });

    $("#File-Save-As").click(function() {
        var name = prompt("New filename:");

        console.log("Saving As: " + name);
        data = send_api("file_save_as", "file=" + name);

        refresh_file_selector();
    });

    $("#File-Delete").click(function() {
        var name = $("#File-List").val();

        console.log("Deleting: " + name);
        data = send_api("file_delete", "file=" + name);

        refresh_all();
    });
}

function refresh_general_settings() {
    baud_list = [ 9600, 19200, 38400, 57600, 115200, 250000 ];
    data = send_api("get_general");

    host = data.host || "";
    port = data.port || "";
    baud = data.baud || 115200;
    headless = data.headless || "";

    console.log( data.headless);

    if (headless == true) {
        headless = "checked";
    }

    s = "<form method='POST' action='set_general'>";

    s += "<h3>General Settings</h3>";
    s += "<label for='host'>Host:</label>";
    s += "<input name='host' value='" + host + "' />";

    s += "<label for='port'>Port:</label>";
    s += "<input name='port' value='" + port + "' />";

    s += "<label for='baud'>Baud:</label>";
    s += build_select(baud_list, baud, null, "Baud-List", "baud", "");

    s += "<label for='default-device-mode'>Device Mode:</label>";
    data = Object.keys(send_api("get_device_mode"));
    current = send_api("get_default_device_mode");
    s += build_select(data, current, null, "Default-Device-Mode", "default-device-mode", "");

    s += "<label for='default-device-mode'>Display Mode:</label>";
    data = Object.keys(send_api("get_display_mode"));
    current = send_api("get_default_display_mode");
    s += build_select(data, current, null, "Default-Display-Mode", "default-display-mode", "");


    s += "<label for='headless'>Headless:</label>";
    s += "<input type='checkbox' name='headless' " + headless + " />";

    s += "<input id='General-Settings-Submit' class='update-button' type='button' value='Update' />";
    s += "</form>"

    $("#General-Settings").html(s);

    $("#General-Settings-Submit").click(function() {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_general_settings();
    });
}

function refresh_arduino_selector() {
    data = Object.keys(send_api("get_arduino"));

    s = build_select(data, null, 10, "Arduino-List", "arduino", "list");
    s += "<input id='Arduino-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Arduino-Delete' class='list-button' type='submit' value='Delete' />"

    console.log(s);
    $("#Arduino-Selector").html(s);

    $("#Arduino-List").change(function () {
        refresh_arduino_details();
    });

    $("#Arduino-New").click(function () {
        var name = prompt("New Arduino:");

        console.log("Adding: " + name);
        data = send_api("new_arduino", "name=" + name);

        refresh_all();
    });

    $("#Arduino-Delete").click(function () {
        var name = $("#Arduino-List").val();

        if (name == null) { return; }

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Arduino-Details").html("");
        refresh_arduino_selector();
    });
}

function refresh_arduino_details() {
    data = send_api("get_arduino", "name=" + $("#Arduino-List").val());
    numbers = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ];

    if ($("#Arduino-List").val() == null || data == null) { return; }

    if (data.default) {
        data.default = "checked";
    } else {
        data.default = "";
    }

    s = "<form method='POST' action='set_arduino'>";

    s += "<h3>Arduino Configuration</h3>";
    s += "<input name='key' type='hidden' value='" + $("#Arduino-List").val() + "' /> ";

    s += "<label for='name'>Name:</label>";
    s += "<input id='Arduino-Name' name='name' value='" + $("#Arduino-List").val() + "' /> ";

    s += "<label for='uuid'>UUID:</label> ";
    s += "<input name='uuid' value='" + data.uuid + "' /> ";

    s += "<label for='bargraphs'>Bargraphs:</label>";
    s += build_select(numbers, data.bargraphs, "", "Bargraph-Count", "bargraphs", "");

    s += "<label for='sevensegments'>Seven Segments:</label>";
    s += build_select(numbers, data.sevensegments, "", "SevenSegment-Count", "sevensegments", "");
    console.log(data.sevensegments);

    s += "<label for='default'>Default:</label> ";
    s += "<input name='default' type='checkbox' name='default' " + data.default + " /> ";

    s += "<input id='Arduino-Details-Submit' class='update-button' type='button' value='Update' /> ";
    s += "</form>";

    console.log(s);
    $("#Arduino-Details").html(s);

    $("#Arduino-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        old_name = $("#Arduino-List").val();
        new_name = $("#Arduino-Name").val()

        console.log(postdata);

        send_api(api, postdata);

        if (old_name != new_name) {
            refresh_arduino_selector();
            $("#Arduino-List").val(new_name);
        }

        refresh_arduino_details();
    });
}

function refresh_display_selector() {
    data = send_api("get_display");
    names = [];

    try {
        for (display of data) {
            names.push(display.name);
        }
    } catch (e) {
        names = [];
    }

    s = build_select(names, null, 10, "Display-List", "display", "list");
    s += "<input id='Display-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Display-Delete' class='list-button' type='submit' value='Delete' />"

    console.log(s);
    $("#Display-Selector").html(s);

    $("#Display-List").change(function () {
        refresh_display_details();
    });

    $("#Display-New").click(function () {
        var name = prompt("New Display:");

        console.log("Adding: " + name);
        data = send_api("new_display", "name=" + name);

        refresh_display_selector()
    });

    $("#Display-Delete").click(function () {
        var name = $("#Display-List").val();

        if (name == null) { return; }

        console.log("Deleting: " + name);
        data = send_api("delete_display", "name=" + name);

        $("#Display-Details").html("");
        refresh_display_selector()
    });
}

function refresh_display_details() {
    data = send_api("get_display", "name=" + $("#Display-List").val());
    types = [ "SevenSegment", "Bargraph" ];

    if ($("#Display-List").val() == null || data == null) { return; }

    if (data.default) {
        data.default = "checked";
    } else {
        data.default = "";
    }

    s = "<form method='POST' action='set_display'>";
    s += "<h3>Display Configuration</h3>";
    s += "<input name='key' type='hidden' value='" + $("#Display-List").val() + "' /> ";
    s += "<label for='name'>Name:</label>";
    s += "<input id='Display-Name' name='name' value='" + data.name + "' />";

    s += "<label for='type'>Type:</label>";
    s += build_select(types, (data.type || "SevenSegment"), null, "Display-Type", "type", "")

    s += "<label for='api'>API:</label>";
    s += "<input name='api' value='" + (data.api || "") + "' />";

    s += "<label class='Bargraph-Only' for='max_api'>API for Max:</label>";
    if ((data.type || "SevenSegment") == "Bargraph") {
        s += "<input id='Max-API' class='Bargraph-Only' name='max_api' value='" + (data.options.max_api || "") + "'  />";
    } else {
        s += "<input id='Max-API' class='Bargraph-Only' name='max_api' />";
    }

    s += "<label class='Bargraph-Only' for='max_value'>Max Value:</label>";
    if ((data.type || "SevenSegment") == "Bargraph") {
        s += "<input id='Max-Value' class='Bargraph-Only' name='max_value' value='" + (data.options.max_value || "") + "'  />";
    } else {
        s += "<input id='Max-Value' class='Bargraph-Only' name='max_value' />";
    }

    s += "<input id='Display-Details-Submit' class='update-button' type='button' value='Update' />";

    console.log(s);
    $("#Display-Details").html(s);

    $("#Display-Type").ready(function() {
        if ($("#Display-Type").val() == "Bargraph") {
            $(".Bargraph-Only").show();
            $(".SevenSegment-Only").hide();
        } else if ($("#Display-Type").val() == "SevenSegment") {
            $(".Bargraph-Only").hide();
            $(".SevenSegment-Only").show();
        }
    });

    $("#Display-Type").change(function() {
        if ($("#Display-Type").val() == "Bargraph") {
            $(".Bargraph-Only").show();
            $(".SevenSegment-Only").hide();
        } else if ($("#Display-Type").val() == "SevenSegment") {
            $(".Bargraph-Only").hide();
            $(".SevenSegment-Only").show();
        }
    });

    $("#Max-API").change(function() {
        if ($("#Max-API").val() == "") {
            $("#Max-Value").prop("disabled",false);
        } else {
            $("#Max-Value").val() == "";
            $("#Max-Value").prop("disabled",true);
        }
    });

    $("#Max-API").ready(function() {
        if ($("#Max-API").val() == "") {
            $("#Max-Value").prop("disabled",false);
        } else {
            $("#Max-Value").val() == "";
            $("#Max-Value").prop("disabled",true);
        }
    });

    $("#Max-Value").change(function() {
        if ($("#Max-Value").val() == "") {
            $("#Max-API").prop("disabled",false);
        } else {
            $("#Max-API").prop("disabled",true);
        }
    });

    $("#Max-Value").ready(function() {
        if ($("#Max-Value").val() == "") {
            $("#Max-API").prop("disabled",false);
        } else {
            $("#Max-API").prop("disabled",true);
        }
    });

    $("#Display-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        old_name = $("#Display-List").val();
        new_name = $("#Display-Name").val()

        console.log(postdata);

        send_api(api, postdata);

        if (old_name != new_name) {
            refresh_display_selector();
            $("#Display-List").val(new_name);
        }

        refresh_display_details();
    });
}

function refresh_device_selector() {
    data = send_api("get_device");
    names = [];

    try {
        for (display of data) {
            names.push(display.name);
        }
    } catch (e) {
        names = [];
    }

    s = build_select(names, null, 10, "Device-List", "device", "list");
    s += "<input id='Device-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Device-Delete' class='list-button' type='submit' value='Delete' />"

    console.log(s);
    $("#Device-Selector").html(s);

    $("#Device-List").change(function () {
        refresh_device_details();
    });

    $("#Device-New").click(function () {
        var name = prompt("New Device:");

        console.log("Adding: " + name);
        data = send_api("new_device", "name=" + name);

        refresh_all();
    });

    $("#Device-Delete").click(function () {
        var name = $("#Device-List").val();

        if (name == null) { return; }

        console.log("Deleting: " + name);
        data = send_api("delete_device", "name=" + name);

        $("#Device-Details").html("");
        refresh_all();
    });
}

function refresh_device_details() {
    data = send_api("get_device", "name=" + $("#Device-List").val());
    types = ["DigitalIn", "DigitalOut", "AnalogIn", "AnalogOut", "Mod", "Joy"];

    console.log(data);
    if ($("#Device-List").val() == null || data == null) { return; }

    s = "<form method='POST' action='set_device'>";
    s += "<input name='key' type='hidden' value='" + $("#Device-List").val() + "' /> ";
    s += "<h3>Device Configuration</h3>";
    s += "<label for='name'>Name:</label>";
    s += "<input id='Device-Name' name='name' value='" + data.name + "' />";

    s += "<label for='api'>API:</label>";
    s += "<input name='api'  value='" + (data.api || "") + "' />";

    s += "<label for='type'>Type:</label>";
    s += build_select(types, (data.type || "DigitalIn"), null, "Device-Type", "type", "")

    s += "<label for='pin' class='pin pin_list'>Pin:</label>";
    s += build_pin_list("Pin-List", "pin", "pin pin_list", (data.pin || null));

    s += "<label for='x' class='joy pin_list'>X:</label>";
    s += build_pin_list("Pin-List-Joy-X", "x", "joy pin_list", (data.x || null));

    s += "<label for='y' class='joy pin_list'>Y:</label>";
    s += build_pin_list("Pin-List-Joy-Y", "y", "joy pin_list", (data.y || null));

    s += "<label for='z' class='joy pin_list'>Z:</label>";
    s += build_pin_list("Pin-List-Joy-Z", "z", "joy pin_list", (data.z || null));

    s += "<label for='button' class='joy pin_list'>Button:</label>";
    s += build_pin_list("Pin-List-Joy-Button", "button", "joy pin_list", (data.button || null));

    s += "<label for='mod-modifier' class='mod pin_list'>Modifier:</label>";
    s += build_pin_list("Pin-List-Mod-Modifier", "modifier", "mod pin_list", (data.modifier || null));

    s += "<label for='mod-indicator' class='mod pin_list'>Indicator:</label>";
    s += build_pin_list("Pin-List-Mod-Indicator", "indicator", "mod pin_list", (data.indicator || null));

    s += "<label for='mod-button' class='mod pin_list'>Button:</label>";
    s += build_pin_list("Pin-List-Mod-Button", "button", "mod pin_list", (data.button || null));

    s += "<br />";
    s += "<input id='Device-Details-Submit' class='update-button' type='button' value='Update' />";

    console.log(s);
    $("#Device-Details").html(s);

    $("#Device-Type").ready(function() {
        if ($("#Device-Type").val() == "Joy") {
            $(".mod, .pin").hide();
            $(".joy").show();
        } else if ($("#Device-Type").val() == "Mod") {
            $(".joy, .pin").hide();
            $(".mod").show();
        } else {
            $(".mod, .joy").hide();
            $(".pin").show();
        }
    });

    $("#Device-Type").change(function() {
        if ($("#Device-Type").val() == "Joy") {
            $(".mod, .pin").hide();
            $(".joy").show();
        } else if ($("#Device-Type").val() == "Mod") {
            $(".joy, .pin").hide();
            $(".mod").show();
        } else {
            $(".mod, .joy").hide();
            $(".pin").show();
        }
    });

    $("#Device-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        old_name = $("#Device-List").val();
        new_name = $("#Device-Name").val()

        console.log(postdata);

        send_api(api, postdata);

        if (old_name != new_name) {
            refresh_device_selector();
            $("#Device-List").val(new_name);
        }

        refresh_device_details();
    });
}

function refresh_device_mode_selector() {
    data = Object.keys(send_api("get_device_mode"));

    s = build_select(data, null, 10, "Device-Mode-List", "device-mode", "list");
    s += "<input id='Device-Mode-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Device-Mode-Delete' class='list-button' type='submit' value='Delete' />"

    console.log(s);
    $("#Device-Mode-Selector").html(s);

    $("#Device-Mode-List").change(function () {
        refresh_device_mode_details();
    });

    $("#Device-Mode-New").click(function () {
        var name = prompt("New Device-Mode:");

        console.log("Adding: " + name);
        data = send_api("new_device_mode", "name=" + name);

        refresh_device_mode_selector();
    });

    $("#Device-Mode-Delete").click(function () {
        var name = $("#Device-Mode-List").val();

        if (name == null) { return; }

        console.log("Deleting: " + name);
        data = send_api("delete_device_mode", "name=" + name);

        $("#Device-Mode-Details").html("");
        refresh_device_mode_selector();
    });
}

function refresh_device_mode_details() {
    // To do
    if ($("#Device-Mode-List").val() == null || data == null) { return; }

    s = "<form method='POST' action='set_device_mode'>";
    s += "<h3>Device Mode Configuration</h3>";
    s += "<label for='arduino'>Arduino:</label>";
    s += "<select name='arduino'>";
    s += "<option>Primary</option>";
    s += "<option>Secondary</option>";
    s += "<option>Tertiary</option>";
    s += "</select>";

    s += "<div class='section'>";
    s += "<h3>Available</h3>";
    s += "<select size='7' class='list'>";
    s += "<option>Joy 1</option>";
    s += "<option>Joy 2</option>";
    s += "<option>Button 1</option>";
    s += "<option>Button 2</option>";
    s += "</select>";

    s += "<input class='list-button' type='submit' value='Add' />";
    s += "</div>";
    s += "<div class='section'>";
    s += "<h3>Configured</h3>";
    s += "<select size='7' class='list'>";
    s += "<option>Joy 1</option>";
    s += "<option>Joy 2</option>";
    s += "<option>Button 1</option>";
    s += "<option>Button 2</option>";
    s += "</select>";

    s += "<input class='list-button' type='submit' value='Remove' />";
    s += "</div>";

    console.log(s);
    $("#Device-Mode-Details").html(s);

    $("#Device-Mode-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });
}

function refresh_display_mode_selector() {
    data = Object.keys(send_api("get_display_mode"));

    s = build_select(data, null, 10, "Display-Mode-List", "display-mode", "list");
    s += "<input id='Display-Mode-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Display-Mode-Delete' class='list-button' type='submit' value='Delete' />"

    console.log(s);
    $("#Display-Mode-Selector").html(s);

    $("#Display-Mode-List").change(function () {
        refresh_arduino_details();
    });

    $("#Display-Mode-New").click(function () {
        var name = prompt("New Display-Mode:");

        console.log("Adding: " + name);
        data = send_api("new_display_mode", "name=" + name);

        refresh_display_mode_selector();
    });

    $("#Display-Mode-Delete").click(function () {
        var name = $("#Display-Mode-List").val();

        if (name == null) { return; }

        console.log("Deleting: " + name);
        data = send_api("delete_display_mode", "name=" + name);

        $("#Display-Mode-Details").html("");
        refresh_display_mode_selector();
    });
}

function refresh_display_mode_details() {
    // To do
    if ($("#Display-Mode-List").val() == null || data == null) { return; }

    s = "<form method='POST' action='set_display_mode>";
    s += "<h3>Display Mode Configuration</h3>";
    s += "<label for='arduino'>Arduino:</label>";
    s += "<select name='arduino'>";
    s += "<option>Primary</option>";
    s += "<option>Secondary</option>";
    s += "<option>Tertiary</option>";
    s += "</select>";

    s += "<div class='section'>";
    s += "<h3>Seven Segment Displays</h3>";
    s += "<select id='display-sevensegment-1'>";
    s += "<option>Apoapsis</option>";
    s += "<option>Periapsis</option>";
    s += "</select>";

    s += "<select id='display-sevensegment-2'>";
    s += "<option>Apoapsis</option>";
    s += "<option>Periapsis</option>";
    s += "</select>";

    s += "<select id='display-sevensegment-3'>";
    s += "<option>Apoapsis</option>";
    s += "<option>Periapsis</option>";
    s += "</select>";

    s += "</div>";

    s += "<div class='section'>";
    s += "<h3>Bargraph Displays</h3>";
    s += "<select id='display-bargraph-1'>";
    s += "<option>Liquid Fuel</option>";
    s += "<option>Oxidizer</option>";
    s += "</select>";

    s += "<select id='display-bargraph-2'>";
    s += "<option>Liquid Fuel</option>";
    s += "<option>Oxidizer</option>";
    s += "</select>";

    s += "<select id='display-bargraph-3'>";
    s += "<option>Liquid Fuel</option>";
    s += "<option>Oxidizer</option>";
    s += "</select>";
    s += "</div>";

    s += "<input class='update-button' type='submit' value='Update' />";


    console.log(s);
    $("#Display-Mode-Details").html(s);

    $("#Display-Mode-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });
}

function refresh_all() {
    refresh_file_selector();
    refresh_general_settings();
    refresh_arduino_selector();
    refresh_arduino_details();
    refresh_display_selector();
    refresh_display_details();
    refresh_device_selector();
    refresh_device_details();
    refresh_device_mode_selector();
    refresh_device_mode_details()
    refresh_display_mode_selector();
    refresh_display_mode_details();
}

$(document).ready(function() {
    $( ".container" ).sortable();
    $( ".container" ).disableSelection();

    refresh_all();
});