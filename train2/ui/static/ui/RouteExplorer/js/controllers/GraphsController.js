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
            window.scope = $scope;
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
                $scope.stops.forEach(function(st) {
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
                        $scope.stat = resp.data;
                        $scope.buildStatDict();
                    }),
                    $http.get('/api/v1/stops/from-to/', {
                        params: {
                            from_stop: $scope.startStop.id,
                            to_stop: $scope.endStop.id,
                        }
                    }).then(function(resp) {
                        $scope.fromToStopsIds = resp.data;
                        $scope.fromToStops = $scope.fromToStopsIds.map(function(stop_id) {
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
                $scope.buildDates();
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
            $scope.buildStatDict = function () {
            };
            $scope.updateChart = function () {
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
            };
            $scope.findDate = function(dates, value) {
                for (var i = 0 ; i < dates.length ; i++) {
                    if (dates[i].value == value) {
                        return dates[i];
                    }
                }
                return null;
            };

            $scope.initData();

            var params = $location.search();
            $scope.input.startDate = $scope.findDate($scope.startDates, params.startDate) || $scope.startDates[$scope.startDates.length-1];
            $scope.input.endDate = $scope.findDate($scope.endDates, params.endDate) || $scope.endDates[$scope.endDates.length-1];
            $scope.input.startStop = Layout.findStop(params.fromStop || 400);
            $scope.input.endStop = Layout.findStop(params.toStop || 3700)
            $scope.refresh();
        }]);





