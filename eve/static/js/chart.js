function initChart(get_data_url, placeholder1, placeholder2) {
    var updateInterval = 30 * 1000,
        data = [],
        totalPoints = 24 * 60 * 60,
        last_time,
        previousPoint = null,
        options = {
            series: {
                lines: {
                    show: true
                }
            },
            yaxis: { min: 0 },
            xaxis: {
                mode: "time",
                timezone: "browser",
                minTickSize: [30, "minute"]
            }
        };

    $.plot(placeholder1, [ ], options);
    $.plot(placeholder2, [ ], options);

    function updateData() {
        var max_count, url;

        if (totalPoints == data.length)
            max_count = 1;
        else
            max_count = totalPoints - data.length;

        url = get_data_url+'?max_count='+max_count;
        if (last_time)
            url += '&last_time='+encodeURIComponent(last_time);
        $.get(url, function (response_data) {
            if (response_data) {
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

                $.plot(placeholder1, [ graph1, graph2 ], options);
                $.plot(placeholder2, [ graph3 ], options);
            }
        });
    }

    function update() {
        updateData();
        setTimeout(update, updateInterval);
    }

    update();
}