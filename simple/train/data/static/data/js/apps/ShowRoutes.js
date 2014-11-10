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

