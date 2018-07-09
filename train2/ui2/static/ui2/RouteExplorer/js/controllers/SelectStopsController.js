angular.module('RouteExplorer').controller('SelectStopsController',
['$scope', '$rootScope', '$location', 'Layout', 'Locale', 'TimeParser',
function($scope, $rootScope, $location, Layout, Locale, TimeParser) {
    'ngInject';
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = Locale.months;

    var dateRange = Layout.getRoutesDateRange();
    $scope.periods = generatePeriods(dateRange.min, dateRange.max);
    $scope.startPeriod = $scope.periods[0];
    $scope.endPeriod = $scope.periods[0];

    $scope.formValid = function() {
        return (
            !!$scope.origin &&
            !!$scope.destination &&
            $scope.origin != $scope.destination &&
            $scope.startPeriod.from <= $scope.endPeriod.to
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
        var period = {
            from: $scope.startPeriod.from,
            to: $scope.endPeriod.to,
            end: $scope.endPeriod.end,
        };
        var fromDate = period.from;
        var toDate = period.end;
        var periodStr = TimeParser.formatPeriod(period);
        Layout.findRoutesByPeriod($scope.origin.id, $scope.destination.id, fromDate, toDate)
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
      var start = new Date(fromDate.getFullYear(), fromDate.getMonth(), 1);
      while (start < toDate) {
        let end = new Date(start.getFullYear(), start.getMonth() + 1, start.getDate());
        var period = {
          from: start,
          to: start,
          end: end,
          name: Locale.months[start.getMonth()].name + " " + start.getFullYear()
        };
        period.toName = Locale.until + period.name;
        periods.push(period);
        start = end;
      }
      periods.reverse();
      return periods;
    }
}]);
