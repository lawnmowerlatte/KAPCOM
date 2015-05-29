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

function build_pin_list() {

    s = "<select name='" + name + "'>";
    s += "<optgroup label='Digital'>";

    for (var i = 0; i<54; i++) {
        s += "<option value='" + i + "'>" + i + "</option>";
    }

    s += "</optgroup>";
    s += "<optgroup label='Analog'>";

    for (var i = 0; i<16; i++) {
        s += "<option value='A" + i + "'>" + i + "</option>";
    }

    s += "</optgroup>";
    s += "</select>";


    return s;
}


function add_handlers() {
    $( ".container" ).sortable();
    $( ".container" ).disableSelection();

    $("#default").ready(function() {
        s = build_pin_list();
        console.log($( s ));
        this.innerHTML = s;
    });

    $("#File-New").click(function() {
        var name = prompt("New filename:");

        console.log("Creating: " + name);
        data = send_api("file_new", "file=" + name);

        refresh_all();
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

        refresh_file_selector();
    });

    $("#General-Settings-Submit").click(function() {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_general_settings();
    });

    // ---------------------------- //

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

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Arduino-Details").html("");
        refresh_all();
    });

    $("#Arduino-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });

    // ---------------------------- //

    $("#Display-List").change(function () {
        refresh_arduino_details();
    });

    $("#Display-New").click(function () {
        var name = prompt("New Display:");

        console.log("Adding: " + name);
        data = send_api("new_arduino", "name=" + name);

        refresh_all();
    });

    $("#Display-Delete").click(function () {
        var name = $("#Display-List").val();

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Display-Details").html("");
        refresh_all();
    });

    $("#Display-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });

    // ---------------------------- //

    $("#Device-List").change(function () {
        refresh_arduino_details();
    });

    $("#Device-New").click(function () {
        var name = prompt("New Device:");

        console.log("Adding: " + name);
        data = send_api("new_arduino", "name=" + name);

        refresh_all();
    });

    $("#Device-Delete").click(function () {
        var name = $("#Device-List").val();

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Device-Details").html("");
        refresh_all();
    });

    $("#Device-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });

    // ---------------------------- //

    $("#Device-Mode-List").change(function () {
        refresh_arduino_details();
    });

    $("#Device-Mode-New").click(function () {
        var name = prompt("New Device-Mode:");

        console.log("Adding: " + name);
        data = send_api("new_arduino", "name=" + name);

        refresh_all();
    });

    $("#Device-Mode-Delete").click(function () {
        var name = $("#Device-Mode-List").val();

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Device-Mode-Details").html("");
        refresh_all();
    });

    $("#Device-Mode-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });

    // ---------------------------- //

    $("#Display-Mode-List").change(function () {
        refresh_arduino_details();
    });

    $("#Display-Mode-New").click(function () {
        var name = prompt("New Display-Mode:");

        console.log("Adding: " + name);
        data = send_api("new_arduino", "name=" + name);

        refresh_all();
    });

    $("#Display-Mode-Delete").click(function () {
        var name = $("#Display-Mode-List").val();

        console.log("Deleting: " + name);
        data = send_api("delete_arduino", "name=" + name);

        $("#Display-Mode-Details").html("");
        refresh_all();
    });

    $("#Display-Mode-Details-Submit").click(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        console.log(postdata);

        send_api(api, postdata);

        refresh_arduino_details();
    });
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

    add_handlers();
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

    s += "<label for='host'>Host:</label>";
    s += "<input name='host' value='" + host + "' />";

    s += "<label for='port'>Port:</label>";
    s += "<input name='port' value='" + port + "' />";

    s += "<label for='baud'>Baud:</label>";
    s += build_select(baud_list, baud, null, "Baud-List", "baud", "");

    s += "<label for='headless'>Headless:</label>";
    s += "<input type='checkbox' name='headless' " + headless + " />";

    s += "<input id='General-Settings-Submit' class='update-button' type='button' value='Update' />";
    s += "</form>"

    $("#General-Settings").html(s);

    add_handlers();
}

function refresh_arduino_selector() {
    data = Object.keys(send_api("get_arduino"));

    s = build_select(data, null, 10, "Arduino-List", "arduino", "list");
    s += "<input id='Arduino-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Arduino-Delete' class='list-button' type='submit' value='Remove' />"

    console.log(s);
    $("#Arduino-Selector").html(s);

    add_handlers();
}

function refresh_arduino_details() {
    data = send_api("get_arduino", "name=" + $("#Arduino-List").val());
    numbers = [ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ];

    if (data == null) { return; }

    if (data.default) {
        data.default = "checked";
    } else {
        data.default = "";
    }

    s = "<form method='POST' action='set_arduino'>";
    s += "<input name='key' type='hidden' value='" + $("#Arduino-List").val() + "' /> ";

    s += "<label for='name'>Name:</label>";
    s += "<input name='name' value='" + $("#Arduino-List").val() + "' /> ";

    s += "<label for='uuid'>UUID:</label> ";
    s += "<input name='uuid' value='" + data.uuid + "' /> ";

    s += "<label for='bargraphs'>Bargraphs:</label> ";
    s += build_select(numbers, data.bargraphs, "", "Bargraph-Count", "bargraphs", "");

    s += "<label for='sevensegments'>Seven Segments:</label> ";
    s += build_select(numbers, data.sevensegments, "", "SevenSegment-Count", "sevensegments", "");
    console.log(data.sevensegments);

    s += "<label for='default'>Default:</label> ";
    s += "<input name='default' type='checkbox' name='default' " + data.default + " /> ";

    s += "<input id='Arduino-Details-Submit' class='update-button' type='button' value='Update' /> ";
    s += "</form>";

    console.log(s);
    $("#Arduino-Details").html(s);

    add_handlers();
}

function refresh_display_selector() {
    data = send_api("get_display");
    names = [];

    for (display of data) {
        names.push(display.name);
    }

    s = build_select(names, null, 10, "Display-List", "display", "list");
    s += "<input id='Display-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Display-Delete' class='list-button' type='submit' value='Remove' />"

    console.log(s);
    $("#Display-Selector").html(s);

    add_handlers();
}

function refresh_device_selector() {
    data = send_api("get_device");
    names = [];

    for (display of data) {
        names.push(display.name);
    }

    s = build_select(names, null, 10, "Device-List", "device", "list");
    s += "<input id='Device-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Device-Delete' class='list-button' type='submit' value='Remove' />"

    console.log(s);
    $("#Device-Selector").html(s);

    add_handlers();
}

function refresh_device_mode_selector() {
    data = Object.keys(send_api("get_device_mode"));

    s = build_select(data, null, 10, "Device-Mode-List", "device-mode", "list");
    s += "<input id='Device-Mode-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Device-Mode-Delete' class='list-button' type='submit' value='Remove' />"

    console.log(s);
    $("#Device-Mode-Selector").html(s);

    add_handlers();
}

function refresh_display_mode_selector() {
    data = Object.keys(send_api("get_display_mode"));

    s = build_select(data, null, 10, "Display-Mode-List", "display-mode", "list");
    s += "<input id='Display-Mode-New' class='list-button' type='submit' value='Add' />";
    s += "<input id='Display-Mode-Delete' class='list-button' type='submit' value='Remove' />"

    console.log(s);
    $("#Display-Mode-Selector").html(s);

    add_handlers();
}


function refresh_all() {
    refresh_file_selector();
    refresh_general_settings();
    refresh_arduino_selector();
    refresh_arduino_details();

    refresh_display_selector();

    refresh_device_selector();

    refresh_device_mode_selector();

    refresh_display_mode_selector();
}

$(document).ready(function() {
    refresh_all();
    add_handlers();
});