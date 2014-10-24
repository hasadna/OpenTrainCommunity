var app = angular.module('FromTo', ['my.filters','my.services']);

app.controller('FromToController', ['$scope', 'MyHttp',
function($scope, MyHttp) {
    $scope.hello = 'Hello';
}]);

