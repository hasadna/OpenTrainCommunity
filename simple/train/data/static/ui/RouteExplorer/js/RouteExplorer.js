var baseDir = '/static/ui/RouteExplorer';
var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap', 'ui.bootstrap.buttons']);

app.config(['$routeProvider',
function($routeProvider) {

    var templateUrl = function(templateName) {
        return baseDir + '/tpls/' + templateName + '.html';
    };

    $routeProvider
        .when('/', {
            templateUrl: templateUrl('SelectStops'),
            controller: 'SelectStopsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/select-route/:origin/:destination', {
            templateUrl: templateUrl('SelectRoute'),
            controller: 'SelectRouteController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/route-details/:stop_ids', {
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


app.controller('SelectStopsController', ['$scope', '$location', 'Layout',
function($scope, $location, Layout) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;

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
        $location.path('/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
    };
}]);

app.controller('SelectRouteController', ['$scope', '$location', '$route', 'Layout',
function($scope, $location, $route, Layout) {
    $scope.stops = Layout.getStops();
    var origin = Layout.findStop($route.current.params.origin);
    var destination = Layout.findStop($route.current.params.destination);

    var routes = Layout.findRoutes(origin.id, destination.id);
    if (routes.length > 1)
        collapseRoutes(routes);
    $scope.routes = routes;

    $scope.isCollapsed = function(value) {
        return angular.isArray(value);
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.name;
    };

    $scope.collapsedText = function(stops) {
        return "\u2022".repeat(stops.length);
    };

    $scope.barWidth = function(route) {
        var percentWidth = route.count * 100.0 / $scope.routes[0].count;

        if (percentWidth < 1.0)
            return "1px";

        return percentWidth + "%";
    };

    $scope.goToRouteDetails = function(route) {
        $location.path('/route-details/' + route.stops.join(','));
    };

    function collapseRoutes(routes) {
        var commonStops = findCommonStops(countStopFrequencies(routes), routes.length);

        for (var routeIndex in routes) {
            routes[routeIndex].stops = collapseStops(routes[routeIndex].stops, commonStops);
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

        function collapseStops(stops, commonStops) {
            var collapsed = [];
            var accumulator;

            for (var i in stops) {
                var stopId = stops[i];
                if (i > 0 && i < stops.length - 1 && commonStops[stopId]) {
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
    var stopList = $route.current.params.stop_ids;
    var stopIds = stopList.split(',');
    var statsMap = {};

    $scope.loaded = false;
    $scope.stopIds = stopIds;
    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];

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

    $http.get('/api/path-info-full', { params: { stop_ids: stopList } })
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
