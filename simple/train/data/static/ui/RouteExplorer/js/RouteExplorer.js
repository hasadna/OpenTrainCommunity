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
        .otherwise({
            redirectTo: '/'
        });
}]);

app.controller('SelectRouteController', ['$scope', 'Layout',
function($scope, Layout) {
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

        return stop.name;
    };

    $scope.barWidth = function(path) {
        var percentWidth = path.count * 100.0 / $scope.paths[0].count;

        if (percentWidth < 1.0)
            return "1px";

        return percentWidth + "%";
    };

    $scope.$watch('origin', function() { $scope.paths = findMatchingPaths(); });
    $scope.$watch('destination', function() { $scope.paths = findMatchingPaths(); });

    function findMatchingPaths() {
        if (!$scope.stopsSelected())
            return null;

        return Layout.findPaths($scope.origin.id, $scope.destination.id);
    }
}])
