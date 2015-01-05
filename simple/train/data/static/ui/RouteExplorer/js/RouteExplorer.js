var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap']);

app.config(['$routeProvider',
function($routeProvider) {
    var baseDir = '/static/ui/RouteExplorer';
    $routeProvider
        .when('/', {
            templateUrl: baseDir + '/tpls/SelectRoute.html',
            controller: 'SelectRouteController'
        })
        .otherwise({
            redirectTo: '/'
        });
}]);

app.controller('SelectRouteController', ['$scope', '$http',
function($scope, $http) {
    $scope.stops = [];
    var routes = [];

    $scope.origin = null;
    $scope.destination = null;

    $http.get('/api/stops')
        .success(function(data) {
            $scope.stops = data.map(function(s) { return { id: s.stop_id, name: s.stop_name, shortName: s.stop_short_name }; });
        });

    $http.get('/api/all-routes')
        .success(function(data) {
            routes = data.map(function(r) { return {
                stops: r.stops.map(function(s) { return s.stop_id; }),
                count: r.count
            }});
        });

    $scope.matchingRoutes = function(r) {
        if (!$scope.origin || !$scope.destination)
            return null;

        return routes.filter(function(r) {
            var originIndex = r.stops.indexOf($scope.origin.id);
            var destinationIndex = r.stops.indexOf($scope.destination.id);

            if (originIndex < 0 || destinationIndex < 0)
                return false;

            if (originIndex > destinationIndex)
                return false;

            return true;
        });
    }
}])
