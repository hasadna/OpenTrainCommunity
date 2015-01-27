var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap']);

app.config(['$routeProvider',
function($routeProvider) {
    var baseDir = '/static/ui/RouteExplorer';
    $routeProvider
        .when('/', {
            templateUrl: baseDir + '/tpls/SelectRoute.html',
            controller: 'SelectRouteController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/route-details/:stop_ids', {
            templateUrl: baseDir + '/tpls/RouteDetails.html',
            controller: 'RouteDetailsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .otherwise({
            redirectTo: '/'
        });
}]);

app.controller('SelectRouteController', ['$scope', '$location', 'Layout',
function($scope, $location, Layout) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;

    $scope.stopsSelected = function() {
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

        return stop.shortName;
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

    $scope.$watch('origin', updateMatchingRoutes);
    $scope.$watch('destination', updateMatchingRoutes);

    function updateMatchingRoutes() {
        $scope.routes = findMatchingRoutes();
    }

    function findMatchingRoutes() {
        if (!$scope.stopsSelected())
            return null;

        return Layout.findRoutes($scope.origin.id, $scope.destination.id);
    }
}]);

app.controller('RouteDetailsController', ['$scope', '$route', '$http', 'Layout',
function($scope, $route, $http, Layout) {
    $scope.loaded = false;

    $http.get('/api/path-info', { params: { stop_ids: $route.current.params['stop_ids'] } })
        .success(function(data) {
            $scope.stats = data;
            $scope.loaded = true;
        });

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

            return stop.shortName;
    }
}]);

app.filter('duration', function() {
    return function(seconds) {
        seconds = Math.trunc(seconds);

        var minutes = Math.trunc(seconds / 60);
        seconds -= minutes * 60;
        var hours = Math.trunc(minutes / 60);
        minutes -= hours * 60;

        var res = seconds + "s";
        if (minutes != 0 || hours != 0)
            res = minutes + "m " + res;

        if (hours != 0)
            res = hours + "h " + res;

        return res;
    }
});
