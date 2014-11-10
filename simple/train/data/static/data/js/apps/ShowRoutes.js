var app = angular.module('ShowRoutes', ['my.filters','my.services','my.directives']);

app.controller('ShowRoutesController', ['$scope', 'MyHttp',
function($scope, MyHttp) {
    $scope.routes = [];
    $scope.refreshRoutes = function() {
        MyHttp.get('/api/all-routes/').success(function(data) {
            $scope.routes = data;
        });
    }
    $scope.refreshRoutes();
}]);

app.controller('RouteController', ['$scope', 'MyHttp',
function($scope, MyHttp) {
    $scope.expanded = false;
    $scope.expand = function() {
        console.log('expand()');
        $scope.expanded = true;
        $scope.getRouteInfo();
    }
    $scope.collapse = function() {
        $scope.expanded = false;
    }
    $scope.stop_ids = $scope.route.stops.map(function(s) {
        return s.gtfs_stop_id;
    });
    $scope.getRouteInfo = function() {
        MyHttp.get('/api/route-info/',{
            stop_ids : $scope.stop_ids.join(','),
        }).success(function(data) {
            $scope.routeInfo = data;
        });
    }
}]);
