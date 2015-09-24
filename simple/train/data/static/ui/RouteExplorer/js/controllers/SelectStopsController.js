angular.module('RouteExplorer').controller('SelectStopsController',
['$scope', '$rootScope', '$location', 'Layout',
function($scope, $rootScope, $location, Layout) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = [
        'ינואר',
        'פברואר',
        'מרץ',
        'אפריל',
        'מאי',
        'יוני',
        'יולי',
        'אוגוסט',
        'ספטמבר',
        'אוקטובר',
        'נובמבר',
        'דצמבר'
    ].map(function(v, i) { return { value: i + 1, name: v }; });

    var today = new Date();
    var lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
    $scope.month = lastMonth.getMonth() + 1; // We're using 1-based months vs JavaScript's 0-based
    $scope.year = lastMonth.getFullYear();
    $scope.minYear = 2013;
    $scope.maxYear = $scope.year;

    $scope.formValid = function() {
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

    $scope.goToRoutes = function() {
        $scope.noRoutes = false;
        $scope.loading = true;
        Layout.findRoutesByDate($scope.origin.id, $scope.destination.id, $scope.year, $scope.month)
            .then(function(routes) {
                if (routes.length === 0) {
                    $scope.noRoutes = true;
                } else if (routes.length == 1) {
                    $location.path('/' + $scope.year + '/' + $scope.month + '/routes/' + routes[0].id);
                } else {
                    $location.path('/' + $scope.year + '/' + $scope.month + '/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };

    $scope.dismissError = function() {
        $scope.noRoutes = false;
    };
}]);
