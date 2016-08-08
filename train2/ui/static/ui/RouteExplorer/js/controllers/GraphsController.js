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
        name: 'שביעי',
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
    ['$scope', '$http', '$q', 'Layout', 'daysTable', 'hoursList', 'monthNames',
        function ($scope,
                  $http,
                  $q,
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
                        value: '1/' + s[0] + '/' + s[1],
                    });
                    var ns = s[0] == 12 ? [1, s[1] + 1] : [s[0] + 1, s[1]];
                    $scope.endDates.push({
                        name: monthNames[s[0]] + ' ' + s[1],
                        value: '1/' + ns[0] + '/' + ns[1],
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
            $scope.initData().then(function () {
                $scope.input.startDate = $scope.startDates[10];
                $scope.input.endDate = $scope.endDates[11];
                $scope.input.selectedRoute = $scope.findRoute(10);
                $scope.refresh();
            });
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
                $scope.chartPerDay = {
                    options: {
                        chart: {
                            type: 'line'
                        },
                        title: {
                            text: 'איחור בחתך יומי'
                        }
                    },
                    xAxis: {
                        categories: stopNames,
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
                        }
                    },
                    xAxis: {
                        categories: stopNames,
                    },
                    series: []
                };
                daysTable.forEach(function (di) {
                    $scope.chartPerDay.series.push({
                        name: di.name,
                        data: $scope.perDayDict[di.value].stops.map(function (si) {
                            return 100 * si.arrival_late_pct;
                        })
                    })
                });
                hoursList.forEach(function (hl) {
                    var hlName = "";
                    if (angular.isArray(hl)) {
                        hlName = ''  + hl[0] % 24 + '-' + hl[1] % 24;
                    } else {
                        hlName = 'שבועי';
                    }
                    $scope.chartPerHour.series.push({
                        name: hlName,
                        data: $scope.perHourDict[hl.toString()].stops.map(function (si) {
                            return 100 * si.arrival_late_pct;
                        })
                    })
                });
            };
        }]);





