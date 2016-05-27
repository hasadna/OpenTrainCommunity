"use strict";
$(function () {
    function getPalette20() {
        let palette = [
            '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a',
            '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94',
            '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d',
            '#17becf', '#9edae5'];
        return [...palette.filter((e, idx) => idx % 2 == 0),...palette.filter((e, idx) => idx % 2 == 1)]
    }

    const PALETTE20 = getPalette20();

    class Data {
        constructor(routeId, startDate, endDate) {
            this.routeId = routeId;
            this.startDate = startDate;
            this.endDate = endDate;
            window.data = this;
        }

        getStopNames() {
            return this.route.stops.map(s=>s.heb_stop_names[0]);
        }

        getStatByDay() {
            return this.stat.filter(st => st.info.hours == "all");
        }

        loadData() {
            var cbs = [
                {
                    field: 'stat',
                    url: 'http://otrain.org/api/v1/stats/route-info-full/?format=json',
                    data: {
                        from_date: this.startDate,
                        'to_date': this.endDate,
                        'route_id': this.routeId,
                    }
                },
                {
                    field: 'stops',
                    url: 'http://otrain.org/api/v1/stops/'
                },
                {
                    field: 'route',
                    url: 'http://otrain.org/api/v1/routes/' + this.routeId + '/'
                },
            ];
            var callbacks = cbs.map(function (x) {
                return $.ajax({
                    url: x.url,
                    data: x.data,
                });
            });
            $.when(...callbacks).done((...resps) => {
                var data = {};
                cbs.forEach((cb, idx) => {
                    this[cb.field] = resps[idx][0];
                });
                $("#spinner").remove();
                $("#canvas-div").show();
                this.refreshDetails();
                refreshChart(this)
            });
        };

        refreshDetails(data) {
            $("#details").empty();
            $("#details").append("<li class='list-group-item'>Route ID: " + this.route.id + "</li>");
            $("#details").append("<li class='list-group-item'>Start date: " + this.startDate + "</li>");
            $("#details").append("<li class='list-group-item'>End date: " + this.endDate + "</li>");
        }
    }
    var refreshChart = function(data) {
        var labels = {
            '1': 'Sun',
            '2': 'Mon',
            '3': 'Tue',
            '4': 'Wed',
            '5': 'Thu',
            '6': 'Fri',
            '7': 'Sat',
            'all': 'ALL'
        };
        var stops = data.getStopNames();
        var ctx = $("#main-canvas");
        var datasets = [];
        var stats = data.getStatByDay();
        for (let i = 0 ; i < stats.length ; i++) {
            let stat = stats[i];
            var isTotal = stat.info.week_day == 'all';
            let color = PALETTE20[i];
            if (isTotal) {
                color = "rgba(0,0,0,0.2)";
            }
            let data = stat.stops.map(stop => (stop.arrival_late_pct*100).toFixed(1));
            var dataset = {
                label: labels[stat.info.week_day],
                fill: false,
                data: data,
                backgroundColor: color,
                borderColor: color,
                pointBorderColor: color,
                pointRadius: 5,
            }
            if (isTotal) {
                //dataset['borderDash'] = [5,5,5,5];
                dataset['borderWidth'] = 20;
            }
            datasets.push(dataset);
        }
        var data = {
            labels: stops,
            datasets: datasets,
        };
        var myLineChart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: {
            }
        });
    };
    var getParams = function(){
        var search = location.search.substring(1);
        var parts = search.split("&");
        var result = {};
        for (let p of parts) {
            let [key, value] = p.split("=");
            result[key] = decodeURIComponent(value);
        }
        return result;
    };
    let params = getParams();
    let d = new Data(params.route_id || 106,
                     params.start || '1/3/2016',
                     params.end || '1/4/2016');
    d.loadData();
});
