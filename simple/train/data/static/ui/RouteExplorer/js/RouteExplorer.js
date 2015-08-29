var baseDir = '/static/ui/RouteExplorer';
var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap', 'ui.bootstrap.buttons']);

app.config(['$routeProvider',
function($routeProvider) {

    var templateUrl = function(templateName) {
        return baseDir + '/tpls/' + templateName + '.html';
    };

    $routeProvider
        .when('/', {
            pageId: 'welcome',
            templateUrl: templateUrl('SelectStops'),
            controller: 'SelectStopsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/:year/:month/select-route/:origin/:destination', {
            pageId: 'routes',
            templateUrl: templateUrl('SelectRoute'),
            controller: 'SelectRouteController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/:year/:month/routes/:routeId', {
            pageId: 'route',
            templateUrl: templateUrl('RouteDetails'),
            controller: 'RouteDetailsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            },
            reloadOnSearch: false
        })
        .otherwise({
            redirectTo: '/'
        });
}]);

app.controller('AppController', ['$scope', '$location',
function($scope, $location) {
    $scope.share = function(prefix) {
        var url = prefix + encodeURIComponent('http://otrain.org/#' + $location.url());
        window.open(url, 'sharePopup', 'width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no');
    };

    $scope.$on('$routeChangeSuccess', function(e, route) {
        $scope.bodyClass = route.pageId ? 'rex-page-' + route.pageId : null;
    });
}]);

app.controller('SelectStopsController', ['$scope', '$rootScope', '$location', 'Layout',
function($scope, $rootScope, $location, Layout) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = [
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
    ].map(function(v, i) { return { value: i + 1, name: v }; });

    var today = new Date();
    var lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    $scope.month = lastMonth.getMonth() + 1; // We're using 1-based months vs JavaScript's 0-based
    $scope.year = lastMonth.getFullYear();
    $scope.minYear = 2013;
    $scope.maxYear = $scope.year;

    $scope.formValid = function() {
        return (
            !!$scope.origin &&
            !!$scope.destination &&
            $scope.origin != $scope.destination
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
        Layout.findRoutesByDate($scope.origin.id, $scope.destination.id, $scope.year, $scope.month)
            .then(function(routes) {
                if (routes.length === 0) {
                    $scope.noRoutes = true;
                } else if (routes.length == 1) {
                    $location.path('/' + $scope.year + '/' + $scope.month + '/routes/' + routes[0].id);
                } else {
                    $location.path('/' + $scope.year + '/' + $scope.month + '/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };
}]);

app.controller('SelectRouteController', ['$scope', '$location', '$route', 'Layout',
function($scope, $location, $route, Layout) {
    $scope.stops = Layout.getStops();
    var year = $route.current.params.year;
    var month = $route.current.params.month;
    var origin = Layout.findStop($route.current.params.origin);
    var destination = Layout.findStop($route.current.params.destination);

    Layout.findRoutesByDate(origin.id, destination.id, year, month).then(function(routes) {
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
        return '/#/' + year + '/' + month + '/routes/' + route.id;
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

app.controller('RouteDetailsController', ['$scope', '$route', '$http', '$location', 'LocationBinder', 'Layout',
function($scope, $route, $http, $location, LocationBinder, Layout) {
    var year = $route.current.params.year;
    var month = $route.current.params.month;
    var routeId = $route.current.params.routeId;
    var stopIds = Layout.findRoute(routeId).stops;
    var statsMap = {};

    $scope.loaded = false;
    $scope.stopIds = stopIds;
    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];
    $scope.year = year;
    $scope.month = month;

    $scope.selectedDay = null;
    $scope.days = [
        { abbr: 'א', title: 'ראשון', id: 1 },
        { abbr: 'ב', title: 'שני', id: 2 },
        { abbr: 'ג', title: 'שלישי', id: 3 },
        { abbr: 'ד', title: 'רביעי', id: 4 },
        { abbr: 'ה', title: 'חמישי', id: 5 },
        { abbr: 'ו', title: 'שישי', id: 6 },
        { abbr: 'ש', title: 'שבת', id: 7 }
    ];

    $scope.selectedTime = null;
    $scope.times = [];

    var fromDate = new Date(year, month - 1, 1);
    var toDate = new Date(year, month, 1); // Date constructor wraps around so this works on December as well

    $http.get('/api/route-info-full', { params: { route_id: routeId, from_date: fromDate.getTime(), to_date: toDate.getTime() } })
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

    function selectedStats() {
        var dayId = $scope.selectedDay || 'all';
        var timeId = $scope.selectedTime || 'all';

        var stats = statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId].stops : [];
        return stats;
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

        function formatHour(hour) {
            return ('0' + hour % 24 + '').slice(-2) + ':00';
        }
    }
}]);

app.filter('duration', function() {
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

app.directive("rexPercentBar", function() {
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: baseDir + '/tpls/PercentBar.html'
      };
});

app.factory('LocationBinder', function($location) {
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
});
