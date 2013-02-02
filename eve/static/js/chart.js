var EVA = EVA || {};

EVA.Chart = function (get_data_url, placeholder1, placeholder2) {
    // Consts
    var hourPoints = 60 * 60;
    var dayPoints = 24 * hourPoints;
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
            minTickSize: [30, "minute"]
        }
    };

    var data, totalPoints, last_time;
    var plot1 = $.plot(placeholder1, [ ], options);
    var plot2 = $.plot(placeholder2, [ ], options);

    function pad(num, size) {
        var s = num+"";
        while (s.length < size) s = "0" + s;
        return s;
    }

    function toTZ(date) {
        var tz = date.getTimezoneOffset();
        var h = pad(Math.abs(parseInt(tz / 60)), 2);
        var m = pad(Math.abs(tz % 60), 2);
        var sign = tz < 0 ? "-" : "+";
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
                data = data.slice(data.length - totalPoints);

                last_time = data[data.length - 1][0];

                // zip the generated y values with the x values
                var graph1 = [], graph2 = [], graph3 = [];
                for (var i = 0; i < data.length; ++i) {
                    var date = new Date(data[i][0]);
                    graph1.push([date, data[i][1][0]]);
                    graph2.push([date, data[i][1][1]]);
                    graph3.push([date, data[i][1][2]]);
                }

                plot1.setData([ graph1, graph2 ]);
                plot1.setupGrid();
                plot1.draw();

                plot2.setData([ graph3 ]);
                plot2.setupGrid();
                plot2.draw();
            }
        });
    }

    this.perDay = function () {
        totalPoints = dayPoints;
        var d = new Date();
        d.setSeconds(d.getSeconds() - totalPoints);
        last_time = toTZ(d);
        data = [];
    }

    this.perHour = function () {
        totalPoints = hourPoints;
        var d = new Date();
        d.setSeconds(d.getSeconds() - totalPoints);
        last_time = toTZ(d);
        data = [];
    }

    this.render = function () {
        plot1.setData([ ]);
        plot1.setupGrid();
        plot1.draw();
        plot2.setData([ ]);
        plot2.setupGrid();
        plot2.draw();
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

    this.perDay()

    return this;
}