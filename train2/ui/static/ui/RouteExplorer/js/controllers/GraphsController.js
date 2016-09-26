'use strict';
angular.module('RouteExplorer').constant('daysTable',
    [{
        value: 1,
        name: 'ראשון',
    }, {
        value: 2,
        name: 'שני',
    }, {
        value: 3,
        name: 'שלישי',
    }, {
        value: 4,
        name: 'רביעי',
    }, {
        value: 5,
        name: 'חמישי',
    }, {
        value: 6,
        name: 'שישי',
    }, {
        value: 7,
        name: 'שבת',
    }, {
        value: 'all',
        name: 'שבועי'
    }
    ])
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
        [4, 7],
        [7, 9],
        [9, 12],
        [12, 15],
        [15, 18],
        [18, 21],
        [21, 24],
        [24, 28],
        "all"
    ]
);


angular.module('RouteExplorer').controller('GraphsController',
    ['$scope', '$http', '$q', '$timeout', '$location', 'Layout', 'daysTable', 'hoursList', 'monthNames',
        function ($scope,
                  $http,
                  $q,
                  $timeout,
                  $location,
                  Layout,
                  daysTable,
                  hoursList,
                  monthNames) {
            $scope.wip = true;
            $scope.Layout = Layout;
            $scope.input = {
                graphKind: 'perDay'
            };
            $scope.refresh = function () {
                $scope.wip = true;
                var routeId = $scope.input.selectedRoute.id;
                $scope.routeId = routeId;
                $scope.startDate = $scope.input.startDate.value;
                $scope.endDate = $scope.input.endDate.value;
                $location.search({
                    routeId: $scope.routeId,
                    startDate: $scope.startDate,
                    endDate: $scope.endDate,
                });
                $scope.stops = Layout.getStops();
                var cbs = [
                    $http.get('/api/v1/stats/route-info-full/', {
                        params: {
                            from_date: $scope.startDate,
                            to_date: $scope.endDate,
                            route_id: $scope.routeId,
                        }
                    }).then(function (resp) {
                        $scope.stat = resp.data;
                        $scope.buildStatDict();
                    }),
                    $http.get('/api/v1/routes/' + $scope.routeId + '/').then(function (resp) {
                        $scope.route = resp.data;
                    }),
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
                $scope.buildDates();
                return $scope.buildRoutes();
            };

            $scope.buildRoutes = function () {
                return $http.get('/api/v1/routes/all/').then(function (resp) {
                    var routes = resp.data;
                    var sortedRoutes = routes.map(function (r) {
                        return {
                            id: r.id,
                            from: Layout.findStopName(r.stop_ids[0]),
                            to: Layout.findStopName(r.stop_ids[r.stop_ids.length - 1]),
                            count: r.count
                        }
                    });
                    sortedRoutes.sort(function (s1, s2) {
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
                    $scope.routes = sortedRoutes;
                });
            };
            $scope.buildDates = function () {
                var s = [1, 2015];
                var e = [4, 2016];
                $scope.startDates = [];
                $scope.endDates = [];
                while (s[0] != e[0] || s[1] != e[1]) {
                    $scope.startDates.push({
                        name: monthNames[s[0]] + ' ' + s[1],
                        value: '1-' + s[0] + '-' + s[1],
                    });
                    var ns = s[0] == 12 ? [1, s[1] + 1] : [s[0] + 1, s[1]];
                    $scope.endDates.push({
                        name: monthNames[s[0]] + ' ' + s[1],
                        value: '1-' + ns[0] + '-' + ns[1],
                    });
                    s[0] = s[0] + 1;
                    if (s[0] > 12) {
                        s[0] = 1;
                        s[1]++;
                    }
                }
            };
            $scope.findRoute = function (rid) {
                for (var i = 0; i < $scope.routes.length; i++) {
                    if ($scope.routes[i].id == rid) {
                        return $scope.routes[i];
                    }
                }
                throw "could not find route (from " + $scope.routes.length + ") with id = " + rid;
            };
            $scope.buildStatDict = function () {
                var perDay = $scope.stat.filter(function (st) {
                    return st.info.hours == 'all'
                });
                $scope.perDayDict = {};
                perDay.forEach(function (st) {
                    $scope.perDayDict[st.info.week_day] = st;
                });
                var perHour = $scope.stat.filter(function (st) {
                    return st.info.week_day == 'all'
                });
                $scope.perHourDict = {};
                perHour.forEach(function (st) {
                    var hkey = st.info.hours.toString();
                    $scope.perHourDict[hkey] = st;
                });
            };
            $scope.updateChart = function () {
                window.scope = $scope;
                var stopNames = $scope.route.stops.map(function (stop, idx) {
                    return '' + (1 + idx) + ' - ' + stop.heb_stop_names[0];
                });
                var tooltip = {
                    formatter: function () {
                        var prec = Math.round(this.y*100)/100;
                        return '<span dir="rtl"><b>' + this.x + '</b>' + '<br/>' +
                            '<span>רכבות מאחרות:</span>' + prec + '%' + '<br/>' +
                            '<span>מספר רכבות: </span>' + this.point.numTrips +
                            '</span>';
                    },
                    useHTML: true,
                };
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
                    series: []
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
                    series: []
                };
                daysTable.forEach(function (di) {
                    var data = $scope.perDayDict[di.value].stops.map(function (si, idx) {
                        return {
                            'y': 100 * (si.arrival_late_pct || 0),
                            'enabled': !angular.isUndefined(si.arrival_late_pct),
                            'numTrips': $scope.perDayDict[di.value].info.num_trips
                        }
                    });
                    $scope.chartPerDay.series.push({
                        name: di.name,
                        data: data,
                        //numTrips: $scope.perDayDict[di.value].stops.map(function () {
                        //    return $scope.perDayDict[di.value].info.num_trips;
                        //}),
                    });
                });
                hoursList.forEach(function (hl) {
                    var hlName = "";
                    if (angular.isArray(hl)) {
                        hlName = '' + hl[0] % 24 + '-' + hl[1] % 24;
                    } else {
                        hlName = 'שבועי';
                    }
                    var data = $scope.perHourDict[hl.toString()].stops.map(function (si) {
                        return {
                            'y': 100 * (si.arrival_late_pct || 0),
                            'enabled': !angular.isUndefined(si.arrival_late_pct),
                            'numTrips': $scope.perHourDict[hl.toString()].info.num_trips
                        }
                    });
                    $scope.chartPerHour.series.push({
                        name: hlName,
                        data: data
                    })
                });
            };
            $scope.findDate = function(dates, value) {
                for (var i = 0 ; i < dates.length ; i++) {
                    if (dates[i].value == value) {
                        return dates[i];
                    }
                }
                return null;
            };
            $scope.initData().then(function () {
                var params = $location.search();
                $scope.input.startDate = $scope.findDate($scope.startDates, params.startDate) || $scope.startDates[$scope.startDates.length-1];
                $scope.input.endDate = $scope.findDate($scope.endDates, params.endDate) || $scope.endDates[$scope.endDates.length-1];
                $scope.input.selectedRoute = $scope.findRoute(params.routeId || 10);
                $scope.refresh();
            });
        }]);





