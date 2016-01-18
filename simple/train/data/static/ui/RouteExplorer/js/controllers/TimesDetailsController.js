angular.module('RouteExplorer').controller('TimesDetailsController',
    ['$scope', 'Locale',
function($scope, Locale) {
    $scope.days = Locale.days;
    $scope.hours = Locale.hours;
}]);

