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

function refresh_all() {
    refresh_file_selector();
    refresh_general_settings();

}

$(document).ready(function() {
    refresh_all();
    add_handlers();
});