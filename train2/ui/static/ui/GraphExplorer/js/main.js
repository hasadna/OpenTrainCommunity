$(function () {
    var loadData = function(config) {
        var routeId = 106;
        var url = 'http://otrain.org/api/v1/stats/route-info-full/';
        var cbs = [
            {
                field: 'stat',
                url: url,
                data: {
                    route_id: config.route_id,
                    start_date: config.start_date,
                    end_date: config.end_date,
                },
            },
            {
                field: 'stops',
                url: 'http://otrain.org/api/v1/stops/'
            },
            {
                field: 'route',
                url: 'http://otrain.org/api/v1/routes/' + routeId + '/'
            },
        ];
        var callbacks = cbs.map(function(x) {
            return $.ajax({
                url: x.url,
                data: x.data,
            });
        });
        console.log(callbacks.length);
        $.when.apply($,callbacks).done(function (x1, x2, x3) {
            var resps = [x1,x2,x3]
            var data = {};
            cbs.forEach(function(cb, idx) {
                data[cb.field] = resps[idx][0];
            })
            $("#spinner").remove();
            $("#canvas-div").show();
            console.log(data);
            refreshChart(data)
        });
    };
    var refreshChart = function(data) {
        var ctx = $("#main-canvas");
        var data = {
            labels: ["January", "February", "March", "April", "May", "June", "July"],
            datasets: [
                {
                    label: "My First dataset",
                    fill: false,
                    lineTension: 0.1,
                    backgroundColor: "rgba(75,192,192,0.4)",
                    borderColor: "rgba(75,192,192,1)",
                    borderCapStyle: 'butt',
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "rgba(75,192,192,1)",
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "rgba(75,192,192,1)",
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointHoverBorderWidth: 2,
                    pointRadius: 1,
                    pointHitRadius: 10,
                    data: [65, 59, 80, 81, 56, 55, 40],
                },
                {
                    label: "My Second dataset",
                    fill: false,
                    lineTension: 0.1,
                    backgroundColor: "rgba(75,192,192,0.4)",
                    borderColor: "rgba(75,192,192,1)",
                    borderCapStyle: 'butt',
                    borderDash: [],
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "rgba(75,192,192,1)",
                    pointBackgroundColor: "#fff",
                    pointBorderWidth: 1,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: "rgba(75,192,192,1)",
                    pointHoverBorderColor: "rgba(220,220,220,1)",
                    pointHoverBorderWidth: 2,
                    pointRadius: 1,
                    pointHitRadius: 10,
                    data: [60, 50, 90, 71, 66, 75, 30],
                }
            ]
        };
        var myLineChart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {}
        });
    };
    loadData({
        route_id: 106,
        start_date: '1/3/2016',
        end_date: '1/4/2016'
    });
});
