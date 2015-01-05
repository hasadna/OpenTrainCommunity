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

    $http.get('/api/stops')
        .success(function(data) {
            $scope.stops = data.map(function(s) { return { id: s.stop_id, name: s.stop_name, shortName: s.stop_short_name }; });
        });
}])
