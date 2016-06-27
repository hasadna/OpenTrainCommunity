"use strict";
$(function () {
    function getPalette20() {
        let palette = [
            '#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#98df8a',
            '#d62728', '#ff9896', '#9467bd', '#c5b0d5', '#8c564b', '#c49c94',
            '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d',
            '#17becf', '#9edae5'];
        return [...palette.filter((e, idx) => idx % 2 == 0), ...palette.filter((e, idx) => idx % 2 == 1)]
    }

    const PALETTE20 = getPalette20();

    const DAYS = {
        '1': 'ראשון',
        '2': 'שני',
        '3': 'שלישי',
        '4': 'רביעי',
        '5': 'חמישי',
        '6': 'שישי',
        '7': 'שבת',
        'all': 'הכל'
    };


    class Data {
        constructor(routeId, startDate, endDate) {
            this.routeId = routeId;
            this.startDate = startDate;
            this.endDate = endDate;
        }

        getStopNames() {
            return this.route.stops.map(s=>s.heb_stop_names[0]);
        }

        getStops() {
            return this.route.stops.map(s => ({
                name: s.heb_stop_names[0],
                id: s.stop_id,
            }));
        }

        buildStops() {
            this.stopsById = {};
            for (let stop of this.stops) {
                this.stopsById[stop.stop_id] = stop;
            }
        }

        getStopName(stop_id) {
            return this.stopsById[stop_id].heb_stop_names[0];
        }

        getRoutes() {
            var result = this.routes.map(r => ({
                id: r.id,
                from: this.getStopName(r.stop_ids[0]),
                to: this.getStopName(r.stop_ids[r.stop_ids.length - 1]),
                count: r.count
            }));
            result.sort((s1, s2) => {
                if (s1.from < s2.from) {
                    return -1;
                }
                if (s1.from > s2.from) {
                    return 1;
                }
                if (s1.to < s2.to) {
                    return -1;
                }
                if (s1.to > s2.to) {
                    return 1;
                }
                if (s1.count > s2.count) {
                    return -1; // reverse count
                }
                if (s1.count < s2.count) {
                    return 1; //reverse count
                }
                return 0;
            });
            return result;
        }

        getStatsByKind(kind) {
            if (kind != 'week_day' && kind != 'hours') {
                throw `Illegal kind ${kind}`;
            }
            let other_kind = kind == 'hours' ? 'week_day' : 'hours';
            let result = this.stat.filter(st => st.info[other_kind] == "all");
            result.sort((st1, st2) => {
                let v1, v2;
                if (kind == 'hours') {
                    v1 = st1.info.hours == 'all' ? 100 : st1.info.hours[0];
                    v2 = st2.info.hours == 'all' ? 100 : st2.info.hours[0];
                } else {
                    v1 = st1.info.week_day == 'all' ? 100 : st1.info.week_day;
                    v2 = st2.info.week_day == 'all' ? 100 : st2.info.week_day;
                }
                return v1 - v2;
            });
            return result;
        }

        getStatInfoForLabel(kind, config, stopIndex, kindVal) {
            let stop_id = this.route.stops[stopIndex].gtfs_stop_id;
            let stats = this.getStatsByKind(kind);
            for (let stat of stats) {
                if (stat.info.stop_id == stop_id && config.getLabel(stat.info[kind]) == kindVal) {
                    return stat.info;
                }
            }
            console.error(`ooops did not found for ${stopIndex} ${seqIndex}`);
        }

        loadData() {
            $.when(...callbacks).done((...resps) => {
                var data = {};
                cbs.forEach((cb, idx) => {
                    this[cb.field] = resps[idx][0];
                });
                this.buildStops();
                $("#spinner").remove();
                $("#main-div").show();
                this.refreshDetails();
                this.buildForm(this)
                this.refreshChart('week_day', {
                    getLabel: v => DAYS[v]
                });
                this.refreshChart('hours', {
                    getLabel: v => v == 'all' ? 'הכל' : `${v[1]} - ${v[0]}`
                });
            });
        };

        buildForm() {
            let monthNames = [
                'dummy',
                'ינואר',
                'פברואר',
                'מרץ',
                'אפריל',
                'מאי',
                'יוני',
                'יולי',
                'אוגוסט',
                'ספטמבר',
                'אוקטובר',
                'נובמבר',
                'דצמבר'
            ];
            let routes = this.getRoutes();
            for (let route of routes) {
                let option = $(`<option value="${route.id}">מ${route['from']} ל${route['to']} (${route['count']} נסיעות)</option>`)
                if (route.id == this.routeId) {
                    option.prop('selected', true);
                }
                $("#select_route").append(option);
            }
            let s = [1, 2015];
            let e = [4, 2016];
            let monthYears = [];
            while (s.join('/') != e.join('/')) {
                monthYears.push([s[0], s[1]]);
                s = s[0] == 12 ? [1, s[1] + 1] : [s[0] + 1, s[1]];
            }
            for (let [m,y] of monthYears) {
                let title = `${monthNames[m]} ${y}`
                let [nm, ny] = m == 12 ? [1, y + 1] : [m + 1, y];
                let val = `1/${m}/${y}`;
                let option = $(`<option value=${val}>${title}</option>`);
                if (val == this.startDate) {
                    option.prop('selected', true);
                }
                let nval = `1/${nm}/${ny}`;
                let noption = $(`<option value=${nval}>${title}</option>`)
                if (nval == this.endDate) {
                    noption.prop('selected', true);
                }
                $("#select_from_date").append(option);
                $("#select_to_date").append(noption);
            }
            $("#explore-form").submit(() => {
                let route_id = $("#select_route").val();
                let from_date = $("#select_from_date").val();
                let to_date = $("#select_to_date").val();
                let newHref = window.location.pathname +
                    `?route_id=${route_id}&from_date=${from_date}&to_date=${to_date}`;
                console.log(newHref);
                window.location.href = newHref;
                return false;
            });
        };

        li(html) {
            let li = $('<li class="list-group-item"></li>');
            li.html(html);
            return li;
        }

        refreshDetails(data) {
            $("#details").empty();
            $("#details").append(this.li(`<b>מזהה מסלול</b>: ${this.route.id}`));
            $("#details").append(this.li(`<b>תאריך התחלה</b>: ${this.startDate}`));
            $("#details").append(this.li(`<b>תאריך סיום</b>: ${this.endDate}`));
            $("#details").append(this.li(`<b>מספר נסיעות</b>: ${this.route.trips_count}`));
        }

        refreshChart(kind, config) { // kind week_day or hours
            var stops = this.getStopNames();
            var ctx = $(`#${kind} canvas`);
            var datasets = [];
            var stats = this.getStatsByKind(kind);
            for (let i = 0; i < stats.length; i++) {
                let stat = stats[i];
                var isTotal = stat.info[kind] == 'all';
                let color = PALETTE20[i];
                if (isTotal) {
                    color = "rgba(0,0,0,0.2)";
                }
                let data = stat.stops.map(stop => (stop.arrival_late_pct * 100).toFixed(1)).reverse();
                var dataset = {
                    label: config.getLabel(stat.info[kind]),
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
            let data = {
                labels: stops.map((x, i) => ` ${1 + i} - ${x}`).reverse(),
                datasets: datasets,
            };
            let myLineChart = new Chart(ctx, {
                type: 'line',
                data: data,
                options: {
                    scales: {
                        yAxes: [{
                            scaleLabel: {
                                display: true,
                                labelString: '% רכבות באיחור'
                            }
                        }]
                    },
                    tooltips: {
                        callbacks: {
                            title: (tooltipItems, data) => {
                                if (tooltipItems.length != 1) {
                                    return '???';
                                }
                                let tooltipItem = tooltipItems[0];
                                let day = data.datasets[tooltipItem.datasetIndex].label;
                                if (kind == 'week_day' && day != DAYS['all']) {
                                    day = 'יום ' + day;
                                }
                                return `${tooltipItem.xLabel} - ${day}`;
                            },
                            label: (tooltipItem, data) => {
                                let realIndex = data.labels.length - tooltipItem.index - 1; // we reverse the list
                                let kindVal = data.datasets[tooltipItem.datasetIndex].label;
                                let info = this.getStatInfoForLabel(kind, config, realIndex, kindVal);
                                return `${tooltipItem.yLabel}% איחורים (מתוך ${info.num_trips} נסיעות)`
                            }
                        }
                    }
                }
            });
        };
    }
    var getParams = function () {
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
    let d = new Data(params.route_id || 10,
        params.from_date || '1/3/2016',
        params.to_date || '1/4/2016');
    d.loadData();
});
