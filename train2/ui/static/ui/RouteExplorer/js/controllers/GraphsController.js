'use strict';
angular.module('RouteExplorer').constant('daysTable',
    [{
        value: 0,
        name: 'ראשון',
    }, {
        value: 1,
        name: 'שני',
    }, {
        value: 2,
        name: 'שלישי',
    }, {
        value: 3,
        name: 'רביעי',
    }, {
        value: 4,
        name: 'חמישי',
    }, {
        value: 5,
        name: 'שישי',
    }, {
        value: 6,
        name: 'שבת',
    }])
    //}], {
    //    value: 'all',
    //    name: 'שבועי'
    //}
    //])
    .constant("monthNames", [
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
    ]).constant("hoursList", [
    {
        name: '4-7',
        values: [4, 5, 6]
    },
    {
        name: '7-9',
        values: [7, 8]
    },
    {
        name: '9-12',
        values: [9,10,11],
    },
    {
        name: '12-15',
        values: [12,13,14],
    },
    {
        name: '15-18',
        values: [15,16,17],
    },
    {
        name: '18-21',
        values: [18, 19,20],
    },
    {
        name: '21-24',
        values: [21, 22,23],
    },
    {
        name: '24-4',
        values: [0, 1, 2, 3],
    }
]
);


angular.module('RouteExplorer').controller('GraphsController',
        function ($scope,
                  $http,
                  $q,
                  $timeout,
                  $location,
                  Layout,
                  daysTable,
                  hoursList,
                  monthNames) {
            'ngInject';
            $scope.wip = true;
            $scope.Layout = Layout;
            $scope.input = {
                graphKind: 'perDay'
            };
            $scope.refresh = function () {
                $scope.wip = true;
                $scope.startStop = $scope.input.startStop;
                $scope.endStop = $scope.input.endStop;
                $scope.startDate = $scope.input.startDate.value;
                $scope.endDate = $scope.input.endDate.value;
                $location.search({
                    startStop: $scope.startStop.id,
                    endStop: $scope.endStop.id,
                    startDate: $scope.startDate,
                    endDate: $scope.endDate,
                });
                $scope.stops = Layout.getStops();
                $scope.stopsById = {};
                $scope.stops.forEach(function (st) {
                    $scope.stopsById[st.id] = st;
                });
                var cbs = [
                    $http.get('/api/v1/stats/from-to-full/', {
                        params: {
                            from_date: $scope.startDate,
                            to_date: $scope.endDate,
                            from_stop: $scope.startStop.id,
                            to_stop: $scope.endStop.id,
                        }
                    }).then(function (resp) {
                        $scope.stat = resp.data.table;
                    }),
                    $http.get('/api/v1/stops/from-to/', {
                        params: {
                            from_stop: $scope.startStop.id,
                            to_stop: $scope.endStop.id,
                        }
                    }).then(function (resp) {
                        $scope.fromToStopsIds = resp.data;
                        $scope.fromToStops = $scope.fromToStopsIds.map(function (stop_id) {
                            return $scope.stopsById[stop_id];
                        });
                    })
                ];
                $q.all(cbs).then(function () {
                    $scope.wip = false;
                    $scope.updateChart();
                });
            };
            $scope.getRouteTitle = function (route) {
                return 'מ' + route.from + ' ל' + route.to + ' (' + route.count + ' ' + 'נסיעות' + ')';
            }

            $scope.initData = function () {
                return $scope.buildDates();
            };

            $scope.buildDates = function () {
                return $http.get('/api/v1/general/dates-range').then( (resp) => {
                    let data = resp.data;
                    var s = [data.first_date.month, data.first_date.year];
                    var e = [data.last_date.month, data.last_date.year];
                    $scope.buildDatesRange(s,e);
                });
            };
            $scope.buildDatesRange = function(s,e) {
                $scope.startDates = [];
                $scope.endDates = [];
                while (true) {
                    let abort = false;
                    $scope.startDates.push({
                        name: monthNames[s[0]] + ' ' + s[1],
                        value: '1-' + s[0] + '-' + s[1],
                    });
                    var ns = s[0] == 12 ? [1, s[1] + 1] : [s[0] + 1, s[1]];
                    $scope.endDates.push({
                        name: monthNames[s[0]] + ' ' + s[1],
                        value: '1-' + ns[0] + '-' + ns[1],
                    });
                    if ($scope.startDates.length > 100) {
                        alert("error");
                        return;
                    }
                    if (s[0] == e[0] && s[1] == e[1]) {
                        return;
                    }
                    s = [ns[0], ns[1]];
                }
            };
            $scope.computePerDaySeries = function () {
                var perDay = {};
                $scope.stat.forEach(function (st) {
                    var key = st.stop_id + '-' + st.week_day_local;
                    perDay[key] = perDay[key] || {
                            num_trips: 0,
                            arrival_late_count: 0
                        };
                    perDay[key].num_trips += st.num_trips;
                    perDay[key].arrival_late_count += st.arrival_late_count;

                });
                var result = [];
                daysTable.forEach(function (d) {
                    var data = $scope.fromToStops.map(function (st) {
                        var entry = perDay[st.id + '-' + d.value];
                        var result = {};
                        if (!entry) {
                            result.y = 0;
                            result.numTrips = 0;
                            console.log('no entry for ' + st.id + ' ' + d.value);
                        } else {
                            result.y = entry.arrival_late_count * 100.0 / entry.num_trips;
                            result.numTrips = entry.num_trips;
                        }
                        result.lineName = d.name;
                        return result;
                    });
                    result.push({
                        name: d.name,
                        data: data
                    })
                });
                return result;
            };
            $scope.computePerHoursSeries = function () {
                var perHour = {};
                var hoursMapping = {}
                hoursList.forEach(function(e) {
                    e.values.forEach(function(h) {
                        hoursMapping[h] = e;
                    })
                });
                $scope.stat.forEach(function (st) {
                    var hour_key = hoursMapping[st.hour_local].name;
                    var key = st.stop_id + '-' + hour_key;
                    perHour[key] = perHour[key] || {
                            num_trips: 0,
                            arrival_late_count: 0
                        };
                    perHour[key].num_trips += st.num_trips;
                    perHour[key].arrival_late_count += st.arrival_late_count;

                });
                var result = [];
                hoursList.forEach(function (hl) {
                    var data = $scope.fromToStops.map(function (st) {
                        var entry = perHour[st.id + '-' + hl.name];
                        var result = {};
                        if (!entry) {
                            console.log('no entry for ' + st.id + ' ' + hl.name);
                            result.y = 0;
                            result.numTrips = 0;
                        } else {
                            result.y = entry.arrival_late_count * 100.0 / entry.num_trips;
                            result.numTrips = entry.num_trips;
                        }
                        result.lineName = hl.name;
                        return result;
                    });
                    result.push({
                        name: hl.name,
                        data: data
                    })
                });
                return result;
            }
            $scope.updateChart = function () {
                var stopNames = $scope.fromToStops.map(function (st, idx) {
                    return st.name + ' - ' + (idx + 1);
                });
                $scope.perDaySeries = $scope.computePerDaySeries();
                $scope.perHoursSeries = $scope.computePerHoursSeries();

                var tooltip = {
                    formatter: function () {
                        var prec = Math.round(this.y * 100) / 100;
                        return '<span dir="rtl"><b>' + this.x + '</b>' + '<br/>' +
                                '<span>' + this.point.lineName + '</span><br/>' +
                            '<span>רכבות מאחרות:</span>' + prec + '%' + '<br/>' +
                            '<span>מספר רכבות: </span>' + this.point.numTrips +
                            '</span>';
                    },
                    useHTML: true,
                };
                var series = [
                    {
                        name: '123',
                        data: [10, 20, 5, 5, 5, 10, 20, 30, 15, 15, 15]
                    },
                    {
                        name: '456',
                        data: [8, 8, 8, 12, 7, 20]
                    },
                ];
                $scope.chartPerDay = {
                    options: {
                        chart: {
                            type: 'line'
                        },
                        title: {
                            text: 'איחור בחתך יומי'
                        },
                        tooltip: tooltip,
                    },
                    xAxis: {
                        reversed: true,
                        categories: stopNames,
                        useHTML: true,
                    },
                    yAxis: {
                        opposite: true,
                        useHTML: true,
                        title: {
                            text: 'אחוזי איחור'
                        }
                    },
                    series: $scope.perDaySeries,
                };
                $scope.chartPerHour = {
                    options: {
                        chart: {
                            type: 'line'
                        },
                        title: {
                            text: 'אישור בחתך שעתי'
                        },
                        tooltip: tooltip,
                    },
                    yAxis: {
                        useHTML: true,
                        opposite: true,
                        title: {
                            text: 'אחוזי איחור'
                        }
                    },
                    xAxis: {
                        useHTML: true,
                        reversed: true,
                        categories: stopNames,
                    },
                    tooltip: {
                        useHTML: true
                    },
                    series: $scope.perHoursSeries,
                };
            };
            $scope.findDate = function (dates, value) {
                for (var i = 0; i < dates.length; i++) {
                    if (dates[i].value == value) {
                        return dates[i];
                    }
                }
                return null;
            };

            $scope.initData().then(() => {
                let params = $location.search();
                $scope.input.startDate = $scope.findDate($scope.startDates, params.startDate) || $scope.startDates[$scope.startDates.length - 1];
                $scope.input.endDate = $scope.findDate($scope.endDates, params.endDate) || $scope.endDates[$scope.endDates.length - 1];
                $scope.input.startStop = Layout.findStop(params.startStop || 400);
                $scope.input.endStop = Layout.findStop(params.endStop || 3700)
                $scope.refresh();
            });
        });





