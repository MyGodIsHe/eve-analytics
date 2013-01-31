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
                },
                points: {
                    show: true
                }
            },
            grid: {
                hoverable: true,
                clickable: true
            },
            yaxis: { min: 0 },
            xaxis: {
                mode: "time",
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
            url += '&last_time='+last_time;
        $.get(url, function (response_data) {
            if (response_data) {
                data.push.apply(data, response_data);
                data = data.slice(data.length - totalPoints);

                last_time = data[data.length - 1][0];

                // zip the generated y values with the x values
                var graph1 = [], graph2 = [], graph3 = [];
                for (var i = 0; i < data.length; ++i) {
                    graph1.push([data[i][0], data[i][1][0]]);
                    graph2.push([data[i][0], data[i][1][1]]);
                    graph3.push([data[i][0], data[i][1][2]]);
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

    function plothover(event, pos, item) {
        if (item) {
            if (previousPoint != item.dataIndex) {

                previousPoint = item.dataIndex;

                $("#tooltip").remove();
                var x = item.datapoint[0].toFixed(2),
                    y = item.datapoint[1].toFixed(2);

                showTooltip(item.pageX, item.pageY, y);
            }
        } else {
            $("#tooltip").remove();
            previousPoint = null;
        }
    }

    placeholder1.bind("plothover", plothover);
    placeholder2.bind("plothover", plothover);


    function showTooltip(x, y, contents) {
        $("<div id='tooltip'>" + contents + "</div>").css({
            position: "absolute",
            display: "none",
            top: y + 5,
            left: x + 5,
            border: "1px solid #fdd",
            padding: "2px",
            "background-color": "#fee",
            opacity: 0.80
        }).appendTo("body").fadeIn(200);
    }
}