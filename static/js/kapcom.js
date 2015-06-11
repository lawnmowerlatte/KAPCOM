Chart.defaults.global.animation = false;


var cycles_chart;
var rate_chart;
var frequency_chart;


$(document).ready(function() {
    var cycles_context = $("#Cycles-Chart").get(0).getContext("2d");
    var rate_context = $("#Rate-Chart").get(0).getContext("2d");
    var frequency_context = $("#Frequency-Chart").get(0).getContext("2d");

    cycles_chart = new Chart(cycles_context).Line({
        labels: [],
        datasets: [
            {
                label: "Cycles",
                fillColor: "rgba(181, 232, 235, 1)",
                strokeColor: "rgba(162, 237, 242, 0)",
                pointColor: "rgba(162, 237, 242, 0)",
                pointDotRadius: 0,
                pointDotStrokeWidth: 0
            }
        ]
    });

    rate_chart = new Chart(rate_context).Line({
        labels: [],
        datasets: [
            {
                label: "Rate",
                fillColor: "rgba(181, 232, 235, 1)",
                strokeColor: "rgba(162, 237, 242, 0)",
                pointColor: "rgba(162, 237, 242, 0)",
            }
        ]
    });
    rate_chart.options.scaleLabel = "<%=value%>ms";


    frequency_chart = new Chart(frequency_context).Line({
        labels: [],
        datasets: [
            {
                label: "Frequency",
                fillColor: "rgba(181, 232, 235, 1)",
                strokeColor: "rgba(162, 237, 242, 0)",
                pointColor: "rgba(162, 237, 242, 0)",
            }
        ]
    });
    frequency_chart.options.scaleLabel = "<%=value%>Hz";

});

function build_li(json_data) {
    var s = "<ul>";
    for (var i in json_data) {
        s += "<li>" + json_data[i] + "</li>";
    }
    s += "</ul>";
    return s;
}


function send_api(command, postdata) {
    console.log(command + " : " + postdata);

    request = {
        async: false,
        url: "api/" + command,
        dataType: 'json'
    }

    if (postdata != null) {
        request.data = postdata;
    }


    response = $.ajax(request);
    console.log(response);

    return response.responseJSON;
}

function refresh_all() {
    refresh_files();
    refresh_status();
    refresh_stats()
    refresh_sevensegments();
    refresh_bargraphs();
    refresh_device_mode();
    refresh_display_mode();

    add_handlers();
}


function refresh_status() {
    json_data = send_api("status");

    var s = "<h1>Status: ";
    if (json_data == true) {
        s += "Running</h1>";
        s += "<h2><a href='#' onclick='$.ajax({url: \"api/stop\"}).done(refresh_status());'>Stop</a></h2>";
    } else {
        s += "Stopped</h1>";
        s += "<h2><a href='#' onclick='$.ajax({url: \"api/start\"}).done(refresh_status());'>Start</a></h2>";
    }

    s += "<h2><a href='#' onclick='$.ajax({url: \"api/restart\"}).done(refresh_status());'>Restart</a></h2>";

    $("#Status").html(s);
}

function refresh_sevensegments() {
    json_data = send_api("get_current_display");
    console.log(json_data.responseJSON);

    s = "";

    for (arduino in json_data) {
        s += "<h4>" + arduino + "</h4>";

        if (json_data[arduino] == null) {
            s += "None";

        } else {
             for (display in json_data[arduino]) {
                if (display == "SevenSegment") {
                    s += "<ul>";
                    for (var i in json_data[arduino][display]) {
                        if (json_data[arduino][display][i] != null) {
                            s += "<li class='sevensegment'>" + json_data[arduino][display][i] + "</li>";
                        } else {
                            s += "<li class='sevensegment'>Empty</li>";
                        }
                    }
                    s += "</ul>";


                }
             }
        }
    }

    $("#SevenSegment").html(s);
}


function refresh_bargraphs() {
    json_data = send_api("get_current_display");
    console.log(json_data.responseJSON);

    s = "";

    for (arduino in json_data) {
        s += "<h4>" + arduino + "</h4>";

        if (json_data[arduino] == null) {
            s += "None";

        } else {
            for (display in json_data[arduino]) {
                if (display == "Bargraph") {
                    s += "<ul>";
                    for (var i in json_data[arduino][display]) {
                        if (json_data[arduino][display][i] != null) {
                            s += "<li class='bargraph'>" + json_data[arduino][display][i] + "</li>";
                        } else {
                            s += "<li class='bargraph'>Empty</li>";
                        }
                    }
                    s += "</ul>";


                }
            }
        }
    }

    $("#Bargraph").html(s);
}

function refresh_device_mode() {
    current = send_api("get_current_mode?type=devices");
    json_data = send_api("get_available_modes?type=devices");

    s = "<ul>";
    for (var i in json_data) {
        if (json_data[i] == current) {
            s += "<li><b>" + json_data[i] + "</b></li>";
        } else {
            s += "<li><a href='#' class='api' onclick='$.ajax({url: \"api/set_mode?type=devices&mode=" + json_data[i] + "\"}).done(refresh_all());'>" + json_data[i] + "</a></li>";
        }
    }
    s += "</ul>";
    $("#Device_Modes").html(s);
}

function refresh_display_mode() {
    current = send_api("get_current_mode?type=displays");
    json_data = send_api("get_available_modes?type=displays");

    s = "<ul>";
    for (var i in json_data) {
        if (json_data[i] == current) {
            s += "<li><b>" + json_data[i] + "</b></li>";
        } else {
            s += "<li><a href='#' class='api' onclick='$.ajax({url: \"api/set_mode?type=displays&mode=" + json_data[i] + "\"}).done(refresh_all());'>" + json_data[i] + "</a></li>";
        }
    }
    s += "</ul>";
    $("#Display_Modes").html(s);
}

function refresh_files() {
    current = send_api("get_current_file");

    s = '<img src="static/img/k.png" width="400px" /><center>';
    s += build_select("file", "file", "", "get_available_files", current);
    s += "</center>";

    $("#File-Selector").html(s);
}


function refresh_stats() {
    stats = send_api("stats");
    max_values = 20;

    while (cycles_chart.datasets[0].points.length > max_values) {
        cycles_chart.removeData();
    }

    while (rate_chart.datasets[0].points.length > max_values) {
        rate_chart.removeData();
    }

    while (frequency_chart.datasets[0].points.length > max_values) {
        frequency_chart.removeData();
    }

    cycles_chart.addData([stats.cycles], "");
    rate_chart.addData([stats.duration*1000], "");
    frequency_chart.addData([1/stats.duration], "");
}

function build_select(name, css_id, css_class, api, current) {
    options = send_api(api);

    s = "<select class='" + css_class + "' id='" + css_id + "' + name='" + name + "'>";

    for (option of options) {
        if (option == current) {
            s += '<option value="' + option + '" selected>' + option + '</option>';
        } else {
            s += '<option value="' + option + '">' + option + '</option>';
        }

    }

    s += "</select>";
    return s;
}


function add_handlers() {
    $( "#container" ).sortable();
    $( "#container" ).disableSelection();

    $("select").click(function () {
        send_api("reconfigure?filename=" + this.value);
        refresh_all();
    });



    $("li.bargraph").click(function () {
        current = this.innerHTML;
        address = send_api("get_display?name=" + current);

        s = "<form method='post' action='set_display'>";
        s += "<input type='hidden' name='type' value=" + address.Type + " />";
        s += "<input type='hidden' name='arduino' value=" + address.Arduino + " />";
        s += "<input type='hidden' name='index' value=" + address.Device + " />";
        s += build_select("name", "Bargraph_Selector", "name", "get_available_displays?type=Bargraph", current);
        s += "</form>";

        s += "<form method='post' action='set_format'>";
        s += "<input type='hidden' name='name' value='" + address.Name + "' />";
        s += build_select("format", "Bargraph_Formatter", "format", "get_available_formats?type=Bargraph", address.Format);
        s += "</form>";

        this.innerHTML = s;
        add_handlers();
    });

    $("li.bargraph select").change(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        send_api(api, postdata);

        refresh_all();
    });

    $("li.sevensegment").click(function () {
        current = this.innerHTML;
        address = send_api("get_display?name=" + current);

        s = "<form method='post' action='set_display'>";
        s += "<input type='hidden' name='type' value=" + address.Type + " />";
        s += "<input type='hidden' name='arduino' value=" + address.Arduino + " />";
        s += "<input type='hidden' name='index' value=" + address.Device + " />";
        s += build_select("name", "SevenSegment", "SevenSegment_Selector", "get_available_displays?type=SevenSegment", current);
        s += "</form>";

        this.innerHTML = s;
        add_handlers();
    });

    $("li.sevensegment select").change(function () {
        var postdata = $(this).parents("form").serializeArray();
        var api = $(this).parents("form").attr("action");

        send_api(api, postdata);

        refresh_all();
    });
}

$(document).ready(function() {
    refresh_all();
    start_stat_refresh();
});


function start_stat_refresh() {
    setTimeout(start_stat_refresh, 1000);
    refresh_stats();
}

