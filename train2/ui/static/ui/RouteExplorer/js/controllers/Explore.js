angular.module('RouteExplorer').controller('ExploreController',
['$scope', '$route', '$http', '$location', 'LocationBinder', 'Layout', 'Locale', 'TimeParser',
function($scope, $route, $http, $location, LocationBinder, Layout, Locale, TimeParser) {
    $scope.days = Locale.days;
    $scope.input = {

    }
}]);
