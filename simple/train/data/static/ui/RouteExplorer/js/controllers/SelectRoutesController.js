angular.module('RouteExplorer').controller('SelectRouteController',
['$scope', '$location', '$route', 'Layout',
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
