angular.module('RouteExplorer').controller('SelectStopsController',
['$scope', '$rootScope', '$location', 'Layout', 'Locale',
function($scope, $rootScope, $location, Layout, Locale) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = Locale.months;

    var dateRange = Layout.getRoutesDateRange();
    $scope.periods = generatePeriods(dateRange.min, dateRange.max);
    $scope.period = $scope.periods[0];

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
        var from = $scope.period.from;
        var to = $scope.period.to;
        var periodStr = from.getFullYear() + ('0' + (from.getMonth() + 1)).slice(-2);
        Layout.findRoutesByPeriod($scope.origin.id, $scope.destination.id, from, to)
            .then(function(routes) {
                if (routes.length === 0) {
                    $scope.noRoutes = true;
                } else if (routes.length == 1) {
                    $location.path('/' + periodStr + '/routes/' + routes[0].id);
                } else {
                    $location.path('/' + periodStr + '/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };

    $scope.dismissError = function() {
        $scope.noRoutes = false;
    };

    function generatePeriods(fromDate, toDate) {
      // fromDate=1970-1-1 due to a data bug. This is a quick temporary workaround
      if (fromDate.getFullYear() < 2013) fromDate = new Date(2013, 0, 1);

      var periods = [];
      var from = new Date(fromDate.getFullYear(), fromDate.getMonth(), 1);
      while (from < toDate) {
        to = new Date(from.getFullYear(), from.getMonth() + 1, from.getDate());
        var period = {
          from: from,
          to: to,
          name: Locale.months[from.getMonth()].name + " " + from.getFullYear()
        };
        periods.push(period);
        from = to;
      }
      periods.reverse();
      return periods;
    }
}]);
