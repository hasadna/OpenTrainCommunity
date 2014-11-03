var app = angular.module('ShowTrip', ['my.filters','my.services','my.directives']);

app.controller('ShowTripController', ['$scope', 'MyHttp',
function($scope, MyHttp) {
    $scope.input = {
        tripId : null,
    };
}]);

