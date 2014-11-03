var app = angular.module('ShowTrip', ['my.filters','my.services','my.directives']);

app.controller('ShowTripController', ['$scope', 'MyHttp','$timeout',
function($scope, MyHttp,$timeout) {
    $scope.input = {
        tripId : null,
    };
    $scope.go = function() {
        $scope.tripId = null;
        $timeout(function() {
            $scope.tripId = $scope.input.tripId;
        },100);
    }
}]);

