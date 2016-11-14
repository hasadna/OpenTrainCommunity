(function () {
    var app = angular.module('RouteExplorer', ['ngRoute',
        'ui.bootstrap',
        'ui.bootstrap.buttons',
        'leaflet-directive',
        "highcharts-ng"
    ]);

    app.constant('env', {
        baseDir: '/static/ui/RouteExplorer'
    });

    app.config(['$routeProvider','env',
        function ($routeProvider, env) {

            var templateUrl = function (templateName) {
                return env.baseDir + '/tpls/' + templateName + '.html';
            };

            $routeProvider
                .when('/', {
                    pageId: 'welcome',
                    templateUrl: templateUrl('SelectStops'),
                    controller: 'SelectStopsController',
                    resolve: {'Layout': 'Layout'}
                })
                .when('/about', {
                    pageId: 'about',
                    templateUrl: templateUrl('About')
                })
                .when('/:period/select-route/:origin/:destination', {
                    pageId: 'routes',
                    templateUrl: templateUrl('SelectRoute'),
                    controller: 'SelectRouteController',
                    resolve: {'Layout': 'Layout'},
                    reloadOnSearch: false
                })
                .when('/:period/routes/:routeId', {
                    pageId: 'route',
                    templateUrl: templateUrl('RouteDetails'),
                    controller: 'RouteDetailsController',
                    resolve: {'Layout': 'Layout'},
                    reloadOnSearch: false
                }).when("/heat-map", {
                    pageId: 'heatMap',
                    templateUrl: templateUrl('HeatMap'),
                    controller: 'HeatMapController',
                    reloadOnSearch: false,
                    resolve: {'Layout': 'Layout'},
                }).when("/graphs", {
                    pageId: 'graphs',
                    templateUrl: templateUrl('Graphs'),
                    controller: 'GraphsController',
                    reloadOnSearch: false,
                    resolve: {'Layout': 'Layout'},
                })
                .otherwise({
                    redirectTo: '/'
                });
        }]);
})();

// String.repeat polyfill
// taken from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/repeat#Polyfill
if (!String.prototype.repeat) {
  String.prototype.repeat = function(count) {
    'use strict';
    if (this === null) {
      throw new TypeError('can\'t convert ' + this + ' to object');
    }
    var str = '' + this;
    count = +count;
    if (count != count) {
      count = 0;
    }
    if (count < 0) {
      throw new RangeError('repeat count must be non-negative');
    }
    if (count == Infinity) {
      throw new RangeError('repeat count must be less than infinity');
    }
    count = Math.floor(count);
    if (str.length === 0 || count === 0) {
      return '';
    }
    // Ensuring count is a 31-bit integer allows us to heavily optimize the
    // main part. But anyway, most current (August 2014) browsers can't handle
    // strings 1 << 28 chars or longer, so:
    if (str.length * count >= 1 << 28) {
      throw new RangeError('repeat count must not overflow maximum string size');
    }
    var rpt = '';
    for (;;) {
      if ((count & 1) == 1) {
        rpt += str;
      }
      count >>>= 1;
      if (count === 0) {
        break;
      }
      str += str;
    }
    return rpt;
  };
}

angular.module('RouteExplorer').controller('AppController',
['$scope', '$location',
function($scope, $location) {
    $scope.share = function(prefix) {
        var url = prefix + encodeURIComponent('http://otrain.org/#' + $location.url());
        window.open(url, 'sharePopup', 'width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no');
    };

    $scope.$on('$routeChangeSuccess', function(e, route) {
        $scope.bodyClass = route.pageId ? 'rex-page-' + route.pageId : null;
    });
}]);

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
            $scope.updateChart = function () {
                var stopNames = $scope.fromToStops.map(function(st) {
                    return st.name;
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






angular.module('RouteExplorer').controller('HeatMapController',
    ['$scope', '$http', 'Layout', function ($scope, $http, Layout) {
        $scope.Layout = Layout;
        var ta = $scope.Layout.findStop(4600); // TA HASHALOM
        console.log(ta);
        angular.extend($scope, {
            defaults: {
                scrollWheelZoom: false
            },
            center: {
                lat: ta.latlon[0],
                lng: ta.latlon[1],
                zoom: 10,
            }
        });
        $scope.stops = Layout.getStops();
        $scope.input = {
            stop: $scope.stops[0]
        }
        $scope.paths = [];
        $http.get('/api/v1/heat-map/').then(function (resp) {
            $scope.heatmapData = resp.data;
            //var maxScore = 0;
            //var minScore = 1;

            //$scope.heatmapData.forEach(function(score) {
            //    maxScore = Math.max(score.score, maxScore);
            //    minScore = Math.min(score.score, minScore);
            //});

            $scope.heatmapData.forEach(function (score) {
                var latlng = $scope.Layout.findStop(score.stop_id).latlon;
                var g = 255-Math.floor(255 * score.score);
                var color = 'rgb(255,' + g + ',0)';
                var message = $scope.Layout.findStop(score.stop_id).name + '<br/>' + Math.floor(score.score * 100) / 100;
                $scope.paths.push({
                    color: color,
                    fillColor: color,
                    fillOpacity: 1,
                    type: "circleMarker",
                    stroke: false,
                    radius: 10,
                    latlngs: latlng,
                    message: message,
                    popupOptions: {
                        className: 'ot-popup'
                    }
                });
            });
        });

    }]);



angular.module('RouteExplorer').controller('RouteDetailsController',
['$scope', '$route', '$http', '$location', 'LocationBinder', 'Layout', 'Locale', 'TimeParser',
function($scope, $route, $http, $location, LocationBinder, Layout, Locale, TimeParser) {
    var routeParams = $route.current.params;

    var period = TimeParser.parsePeriod(routeParams.period);
    var startDate = TimeParser.createRequestString(period.from);
    var endDate = TimeParser.createRequestString(period.end);

    var routeId = routeParams.routeId;
    var stopIds = Layout.findRoute(routeId).stops;
    var statsMap = {};

    $scope.exploreHref = 'http://otrain.org/graphs/?route_id=' + routeId +
    '&from_date=' + startDate + '&to_date=' + endDate;

    $scope.loaded = false;
    $scope.stopIds = stopIds;
    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];

    $scope.selectedPeriod = formatMonth(period.from);
    if (period.to > period.from) {
        $scope.selectedPeriod += " \u2014 " + formatMonth(period.to)
    }

    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    $scope.selectRouteUrl = '#/' + routeParams.period + '/select-route/' + $scope.origin + '/' + $scope.destination;

    var previousPeriod = offsetPeriod(period, -1);
    var nextPeriod = offsetPeriod(period, +1);
    var bounds = Layout.getRoutesDateRange();
    var day = 10 * 24 * 60 * 60 * 1000;
    $scope.previousPeriodUrl = bounds.min.getTime() - day < previousPeriod.from.getTime() ? '#/' + TimeParser.formatPeriod(previousPeriod) + '/routes/' + routeId : null;
    $scope.nextPeriodUrl = bounds.max > nextPeriod.to ? '#/' + TimeParser.formatPeriod(nextPeriod) + '/routes/' + routeId : null;

    $http.get('/api/v1/stats/route-info-full', { params: { route_id: routeId, from_date: startDate, to_date: endDate } })
        .success(function(data) {
            loadStats(data);
            $scope.loaded = true;
        });

    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

            return stop.name;
    };

    $scope.isDayEmpty = function(day) {
        var dayId = day.id;
        var dayTimes = statsMap[dayId];

        if (!dayTimes)
            return true;

        for (var time in dayTimes)
            if (dayTimes[time].info.num_trips > 0)
                return false;

        return true;
    };

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.tripCount = function(dayId, timeId) {
      var stats = getStats(dayId, timeId);
      if (!stats)
        return 0;

      return stats.info.num_trips;
    };

    function getStats(dayId, timeId) {
      dayId = dayId || 'all';
      timeId = timeId || 'all';
      return statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId] : null;
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    function loadStats(data) {
        $scope.times = [];
        var timesMap = {};

        for (var i in data) {
            var statGroup = data[i];
            var timeId = statGroup.info.hours == 'all' ? 'all' : statGroup.info.hours[0] + '-' + statGroup.info.hours[1];
            var dayId = statGroup.info.week_day;

            if (!statsMap[dayId])
                statsMap[dayId] = {};

            statsMap[dayId][timeId] = statGroup;

            if (timeId != 'all' && !timesMap[timeId]) {
                var time = {
                    id: timeId,
                    from: formatHour(statGroup.info.hours[0]),
                    to: formatHour(statGroup.info.hours[1])
                };
                timesMap[timeId] = time;
                $scope.times.push(time);
            }
        }
    }

    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function offsetMonth(date, offset) {
        var d = new Date(date);
        d.setMonth(d.getMonth() + offset);
        return d;
    }

    function offsetPeriod(period, offset) {
        var size =
            (period.to.getFullYear() - period.from.getFullYear()) * 12 +
            period.to.getMonth() - period.from.getMonth() + 1;

        return {
            from: offsetMonth(period.from, size * offset),
            to: offsetMonth(period.to, size * offset),
            end: offsetMonth(period.end, size * offset)
        };
    }
}]);

angular.module('RouteExplorer').controller('SelectRouteController',
['$scope', '$http', '$location', '$route', 'Layout', 'TimeParser',
function($scope, $http, $location, $route, Layout, TimeParser) {
    $scope.stops = Layout.getStops();
    var period = TimeParser.parsePeriod($route.current.params.period);
    var origin = Layout.findStop($route.current.params.origin);
    var destination = Layout.findStop($route.current.params.destination);

    $http.get('/api/v1/stats/path-info-full', { params: {
        origin: origin.id,
        destination: destination.id,
        from_date: TimeParser.createRequestString(period.from),
        to_date: TimeParser.createRequestString(period.end) }
    }).success(function(data) {
            loadStats(data);
            $scope.loaded = true;
    });

    var statsMap = {};

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }


    function loadStats(data) {
        $scope.stats = data;
    }

    Layout.findRoutesByPeriod(origin.id, destination.id, period.from, period.end).then(function(routes) {
        if (routes.length > 1)
            collapseRoutes(routes);
        $scope.routes = routes;

    });

    function stopName(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.name;
    }

    $scope.isCollapsed = function(value) {
        return angular.isArray(value);
    };

    $scope.isOrigin = function(stopId) {
        return stopId == origin.id;
    };

    $scope.isDestination = function(stopId) {
        return stopId == destination.id;
    };

    $scope.stopText = function(stopId) {
        if ($scope.isCollapsed(stopId))
            return "\u2022".repeat(stopId.length);

        return stopName(stopId);
    };

    $scope.stopTooltip = function(stopId) {
        if (!$scope.isCollapsed(stopId))
            return null;

        return stopId.map(stopName).join(", ");
    };

    $scope.barWidth = function(route) {
        var percentWidth = route.count * 100.0 / $scope.routes[0].count;

        if (percentWidth < 1.0)
            return "1px";

        return percentWidth + "%";
    };

    $scope.routeUrl = function(route) {
        return '/#/' + $route.current.params.period + '/routes/' + route.id;
    };

    function collapseRoutes(routes) {
        var collapsibleStops = findCommonStops(countStopFrequencies(routes), routes.length);
        delete collapsibleStops[origin.id];
        delete collapsibleStops[destination.id];

        for (var routeIndex in routes) {
            routes[routeIndex].stops = collapseStops(routes[routeIndex].stops, collapsibleStops);
        }

        function countStopFrequencies(routes) {
            var stopFrequencies = {};
            for (var routeIndex in routes) {
                var route = routes[routeIndex];
                for (var i in route.stops) {
                    var stopId = route.stops[i];
                    if (!stopFrequencies[stopId])
                        stopFrequencies[stopId] = 0;
                    stopFrequencies[stopId]++;
                }
            }

            return stopFrequencies;
        }

        function findCommonStops(stopFrequencies, routesCount) {
            var commonStops = {};
            for (var stopId in stopFrequencies)
                if (stopFrequencies[stopId] == routesCount)
                    commonStops[stopId] = true;

            return commonStops;
        }

        function collapseStops(stops, collapsibleStops) {
            var collapsed = [];
            var accumulator;

            for (var i in stops) {
                var stopId = stops[i];
                if (i > 0 && i < stops.length - 1 && collapsibleStops[stopId]) {
                    if (!accumulator) {
                        accumulator = [];
                        collapsed.push(accumulator);
                    }
                    accumulator.push(stopId);
                } else {
                    accumulator = null;
                    collapsed.push(stopId);
                }
            }

            return collapsed;
        }
    }
}]);

angular.module('RouteExplorer').controller('SelectStopsController',
['$scope', '$rootScope', '$location', 'Layout', 'Locale', 'TimeParser',
function($scope, $rootScope, $location, Layout, Locale, TimeParser) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = Locale.months;

    var dateRange = Layout.getRoutesDateRange();
    $scope.periods = generatePeriods(dateRange.min, dateRange.max);
    $scope.startPeriod = $scope.periods[0];
    $scope.endPeriod = $scope.periods[0];

    $scope.formValid = function() {
        return (
            !!$scope.origin &&
            !!$scope.destination &&
            $scope.origin != $scope.destination &&
            $scope.startPeriod.from <= $scope.endPeriod.to
        );
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.name;
    };

    $scope.goToRoutes = function() {
        $scope.noRoutes = false;
        $scope.loading = true;
        var period = {
            from: $scope.startPeriod.from,
            to: $scope.endPeriod.to,
            end: $scope.endPeriod.end,
        };
        var fromDate = period.from;
        var toDate = period.end;
        var periodStr = TimeParser.formatPeriod(period);
        Layout.findRoutesByPeriod($scope.origin.id, $scope.destination.id, fromDate, toDate)
            .then(function(routes) {
                if (routes.length === 0) {
                    $scope.noRoutes = true;
                } else if (routes.length == 1) {
                    $location.path('/' + periodStr + '/routes/' + routes[0].id);
                } else {
                    $location.path('/' + periodStr + '/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };

    $scope.dismissError = function() {
        $scope.noRoutes = false;
    };

    function generatePeriods(fromDate, toDate) {
      // fromDate=1970-1-1 due to a data bug. This is a quick temporary workaround
      if (fromDate.getFullYear() < 2013) fromDate = new Date(2013, 0, 1);

      var periods = [];
      var start = new Date(fromDate.getFullYear(), fromDate.getMonth(), 1);
      while (start < toDate) {
        end = new Date(start.getFullYear(), start.getMonth() + 1, start.getDate());
        var period = {
          from: start,
          to: start,
          end: end,
          name: Locale.months[start.getMonth()].name + " " + start.getFullYear()
        };
        period.toName = Locale.until + period.name;
        periods.push(period);
        start = end;
      }
      periods.reverse();
      return periods;
    }
}]);

angular.module('RouteExplorer').controller('TimesDetailsController',
    ['$scope', '$route', 'Locale','LocationBinder','Layout',
function($scope, $route, Locale, LocationBinder, Layout) {
    Layout.then(function(Layout) {
        $scope.layout = Layout;
    });
    $scope.layout = null;

    var statsMap = {};
    var routeParams = $route.current.params;
    $scope.stopIds = [parseInt(routeParams.origin), parseInt(routeParams.destination)];
    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');
    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    $scope.stopName = function(stopId) {
        if ($scope.layout) {
            var stop = $scope.layout.findStop(stopId);
            if (!stop)
                return null;

            return stop.name;
        } else {
            return null;
        }
    };

    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    $scope.loadStats = function() {
        var data = $scope.stats;
        $scope.times = [];
        var timesMap = {};

        for (var i in data) {
            var statGroup = data[i];
            var timeId = statGroup.info.hours == 'all' ? 'all' : statGroup.info.hours[0] + '-' + statGroup.info.hours[1];
            var dayId = statGroup.info.week_day;

            if (!statsMap[dayId])
                statsMap[dayId] = {};

            statsMap[dayId][timeId] = statGroup;

            if (timeId != 'all' && !timesMap[timeId]) {
                var time = {
                    id: timeId,
                    from: formatHour(statGroup.info.hours[0]),
                    to: formatHour(statGroup.info.hours[1])
                };
                timesMap[timeId] = time;
                $scope.times.push(time);
            }
        }
    };
    $scope.tripCount = function(dayId, timeId) {
      var stats = getStats(dayId, timeId);
      if (!stats)
        return 0;

      return stats.info.num_trips;
    };

    function getStats(dayId, timeId) {
      dayId = dayId || 'all';
      timeId = timeId || 'all';
      return statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId] : null;
    }

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.loadStats();
}]);


angular.module('RouteExplorer').directive("rexPercentBar",
['env',
function(env) {
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: env.baseDir + '/tpls/PercentBar.html'
      };
}]);

angular.module('RouteExplorer').directive("timesDetails",
['env','Layout',
function(env, Layout) {
    return {
        restrict: 'E',
        scope: {
            stats: '='
        },
        controller: 'TimesDetailsController',
        templateUrl: env.baseDir + '/tpls/TimesDetails.html'
      };
}]);

angular.module('RouteExplorer').filter('duration', function() {
    return function(seconds) {
        var negative = false;
        seconds = Math.trunc(seconds);
        if (seconds < 0) {
            negative = true;
            seconds = -seconds;
        }

        var minutes = Math.trunc(seconds / 60);
        seconds -= minutes * 60;
        var hours = Math.trunc(minutes / 60);
        minutes -= hours * 60;

        if (seconds < 10) seconds = '0' + seconds;
        if (minutes < 10 && hours !== 0) minutes = '0' + minutes;

        var res = minutes + ':' + seconds;
        if (hours !== 0)
            res = hours + ':' + res;

        if (negative)
            res = '-' + res;

        return res;
    };
});

angular.module('RouteExplorer').factory('Layout',
['$http', '$q', 'TimeParser',
function($http, $q, TimeParser) {
    var self = this;
    var stops = [];
    var stopsMap = {};
    var routes = [];
    var routesMap = {};

    var loadedPromise = $q.all([
        $http.get('/api/v1/stops')
            .then(function(response) {
                stops = response.data.map(function(s) { return {
                    id: s.stop_id,
                    name: s.heb_stop_names[0],
                    names: s.heb_stop_names,
                    latlon: s.latlon,
                }; });
                stops.forEach(function(s) { stopsMap[s.id] = s; });
            }),

        $http.get('/api/v1/routes/all/')
            .then(function(response) {
                routes = response.data.map(function(r) { return {
                    id: r.id,
                    stops: r.stop_ids,
                    count: r.count,
                    minDate: new Date(r.min_date),
                    maxDate: new Date(r.max_date)
                }; });

                routesMap = routes.reduce(function(m, r) { m[r.id] = r; return m; }, {});
            })
    ]);

    var findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    var findStopName = function(stopId) {
        return findStop(stopId).name;
    };

    var findRoutes = function(routes, originId, destinationId) {
        var matchingRoutes = {};

        routes.forEach(function(r) {
            var originIndex = r.stops.indexOf(originId);
            var destinationIndex = r.stops.indexOf(destinationId);

            if (originIndex < 0 || destinationIndex < 0)
                return;

            if (originIndex > destinationIndex)
                return;

            var routeStops = r.stops;
            var routeId = r.id;

            if (routeId in matchingRoutes)
                matchingRoutes[routeId].count += r.count;
            else {
                matchingRoutes[routeId] = {
                    id: routeId,
                    stops: routeStops,
                    count: r.count
                };
            }
        });

        matchingRoutes = Object.keys(matchingRoutes).map(function(routeId) { return matchingRoutes[routeId]; });
        matchingRoutes.sort(function(r1, r2) { return r2.count - r1.count; });
        return matchingRoutes;
    };

    var findRoutesByPeriod = function(origin, destination, from, to) {
        // TODO use minDate and maxDate from our cached routes to avoid the http request

        var d = $q.defer();
        var matchingRoutes = findRoutes(routes, origin, destination);
        if (matchingRoutes.length === 0) {
            d.resolve([]);
        } else {
            var fromDate = from;
            var toDate = to;

            $http.get('/api/v1/routes/all-by-date', {
                params: {
                    from_date: TimeParser.createRequestString(fromDate),
                    to_date: TimeParser.createRequestString(toDate)
                }
            }).then(function(response) {
                var routesInDate = response.data.map(function(r) {
                    return {
                        id: r.id,
                        stops: r.stop_ids,
                        count: r.count
                    };
                });
                d.resolve(findRoutes(routesInDate, origin, destination));
            }, function(response) { d.reject({ 'msg': 'Error fetching routes', 'response': response }); });
        }

        return d.promise;
    };

    var findRoute = function(routeId) {
        return routesMap[routeId] || null;
    };

    var getRoutesDateRange = function() {
        var max = new Date(1900, 0, 1);
        var min = new Date(2100, 0, 1);

        for (var i in routes) {
            var route = routes[i];
            if (route.count === 0)
              continue;

            if (route.minDate && route.minDate < min) min = route.minDate;
            if (route.maxDate && route.maxDate > max) max = route.maxDate;
        }
        return {
          min: min,
          max: max
        };
    };

    service = {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findRoute: findRoute,
        findStop: findStop,
        findStopName: findStopName,
        findRoutes: function(origin, destination) { return findRoutes(routes, origin, destination); },
        findRoutesByPeriod: findRoutesByPeriod,
        getRoutesDateRange: getRoutesDateRange
    };

    return loadedPromise.then(function() { return service; });
}]);

angular.module('RouteExplorer').constant('Locale', {
  months: [
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
  ].map(function(v, i) { return { id: i + 1, name: v }; }),

  days: [
      { abbr: 'א', name: 'ראשון', id: 1 },
      { abbr: 'ב', name: 'שני', id: 2 },
      { abbr: 'ג', name: 'שלישי', id: 3 },
      { abbr: 'ד', name: 'רביעי', id: 4 },
      { abbr: 'ה', name: 'חמישי', id: 5 },
      { abbr: 'ו', name: 'שישי', id: 6 },
      { abbr: 'ש', name: 'שבת', id: 7 }
  ],
  until: 'עד ל'
});

angular.module('RouteExplorer').factory('LocationBinder',
['$location',
function($location) {
    return {
        bind: function(scope, scopeProperty, locationProperty, parser, formatter) {
            scope[scopeProperty] = $location.search()[locationProperty] || null;

            scope.$watch(scopeProperty, function(value) {
                if (formatter)
                    value = formatter(value);

                $location.search(locationProperty, value);
            });

            scope.$watch(function() { return $location.search()[locationProperty] || null; }, function(value) {
                if (parser)
                    value = parser(value);

                scope[scopeProperty] = value;
            });
        }
    };
}]);

angular.module('RouteExplorer').factory('TimeParser',
[
function() {
    function createRequestString(date) {
        var dd = date.getDate().toString();
        var mm = (date.getMonth()+1).toString();
        var yyyy = date.getFullYear().toString();
        return dd + '/' + mm + '/' + yyyy;
    }

    function parseMonth(monthString) {
        var year = Number(monthString.substr(0, 4));
        var month = Number(monthString.substr(4, 2));
        return new Date(year, month - 1, 1);
    }

    function parsePeriod(periodString) {
        var parts = periodString.split('-', 2);
        var from = parseMonth(parts[0]);
        var to = parts.length > 1 ? parseMonth(parts[1]) : from;
        var end = new Date(to.getFullYear(), to.getMonth() + 1, 1);
        return { from: from, to: to, end: end };
    }

    function formatMonth(date) {
        return date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2);
    }

    function formatPeriod(period) {
        var f = formatMonth(period.from);
        if (period.from < period.to)
            f += '-' + formatMonth(period.to);

        return f;
    }

    return {
        createRequestString: createRequestString,
        parseMonth: parseMonth,
        parsePeriod: parsePeriod,
        formatMonth: formatMonth,
        formatPeriod: formatPeriod
    }
}]);

//# sourceMappingURL=app.js.map
