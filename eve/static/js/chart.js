var EVA = EVA || {};

EVA.Chart = function (get_data_url, placeholder1, placeholder2) {
    // Consts
    var hourPoints = 60;
    var dayPoints = 24 * hourPoints;
    var hourTickSize = [1, "minute"];
    var dayTickSize = [30, "minute"];
    var updateInterval = 30 * 1000;
    var options = {
        grid: {
            borderWidth: 1,
            minBorderMargin: 20,
            backgroundColor: {
                colors: ["#fff", "#e4f4f4"]
            }
        },
        yaxis: { min: 0 },
        xaxis: {
            mode: "time",
            timezone: "browser",
            minTickSize: dayTickSize
        },
        legend: { position: "sw" }
    };

    var data, totalPoints, last_time, plot1, plot2;

    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

    function toTZ(date) {
        var tz = date.getTimezoneOffset();
        var h = pad(Math.abs(parseInt(tz / 60)), 2);
        var m = pad(Math.abs(tz % 60), 2);
        var sign = tz > 0 ? "-" : "+";
        var result = date.toISOString();
        result = result.slice(0, result.length - 1);
        result += sign + h + ":" + m;
        return result;
    }

    function render(max_count) {
        var url = get_data_url+'?max_count='+max_count+'&last_time='+encodeURIComponent(last_time);
        $.get(url, function (response_data) {
            if (response_data && response_data.length != 0) {
                data.push.apply(data, response_data);

                if (data.length > totalPoints)
                    data = data.slice(data.length - totalPoints);
                else {
                    var ln = totalPoints - data.length,
                        empty = [],
                        first_time = data[0][0];
                    for (var i = ln; i > 0; i--) {
                        var dt = new Date(first_time);
                        dt.setMinutes(dt.getMinutes() - i);
                        empty.push([dt, [null,null,null,null]])
                    }
                    empty.push.apply(empty, data);
                    data = empty;
                }

                last_time = data[data.length - 1][0];

                // zip the generated y values with the x values
                var graph1 = [], graph2 = [], graph3 = [], graph4 = [];
                for (var i = 0; i < data.length; ++i) {
                    var date = new Date(data[i][0]);
                    graph1.push([date, data[i][1][0]]);
                    graph2.push([date, data[i][1][1]]);
                    graph3.push([date, data[i][1][2]]);
                    graph4.push([date, data[i][1][3]]);
                }

                plot1.setData([
                    { data: graph1, color: 1, label: "Skip percent" },
                    { data: graph2, color: 2, label: "Duplicate percent by 10 min" } ]);
                plot1.setupGrid();
                plot1.draw();

                plot2.setData([
                    { data: graph3, color: 3, label: "Queue size" },
                    { data: graph4, color: 4, label: "Valid stream size" } ]);
                plot2.setupGrid();
                plot2.draw();
            }
        });
    }

    this.perDay = function () {
        totalPoints = dayPoints;
        var d = new Date();
        d.setMinutes(d.getMinutes() - totalPoints);
        last_time = toTZ(d);
        data = [];
        options.xaxis.minTickSize = dayTickSize;
    }

    this.perHour = function () {
        totalPoints = hourPoints;
        var d = new Date();
        d.setMinutes(d.getMinutes() - totalPoints);
        last_time = toTZ(d);
        data = [];
        options.xaxis.minTickSize = hourTickSize;
    }

    this.render = function () {
        plot1 = $.plot(placeholder1, [ ], options);
        plot2 = $.plot(placeholder2, [ ], options);
        render(totalPoints);
    }

    this.update = function () {
        var max_count, url;

        if (totalPoints == data.length)
            max_count = 1;
        else
            max_count = totalPoints - data.length;

        render(max_count);

        setTimeout(this.update, updateInterval);
    }

    this.perHour();

    plot1 = $.plot(placeholder1, [ ], options);
    plot2 = $.plot(placeholder2, [ ], options);

    return this;
}