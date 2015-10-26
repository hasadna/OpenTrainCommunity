angular.module('RouteExplorer').controller('RouteDetailsController',
['$scope', '$route', '$http', '$location', 'LocationBinder', 'Layout', 'Locale',
function($scope, $route, $http, $location, LocationBinder, Layout, Locale) {
    var year = $route.current.params.year;
    var month = $route.current.params.month;
    var routeId = $route.current.params.routeId;
    var stopIds = Layout.findRoute(routeId).stops;
    var statsMap = {};

    $scope.loaded = false;
    $scope.stopIds = stopIds;
    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];
    $scope.selectedMonth = Locale.months[month - 1].name + ' ' + year;

    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    var fromDate = new Date(year, month - 1, 1);
    var toDate = new Date(year, month, 1); // Date constructor wraps around so this works on December as well

    $http.get('/api/route-info-full', { params: { route_id: routeId, from_date: fromDate.getTime(), to_date: toDate.getTime() } })
        .success(function(data) {
            loadStats(data);
            $scope.loaded = true;
        });

    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

            return stop.name;
    };

    $scope.isDayEmpty = function(day) {
        var dayId = day.id;
        var dayTimes = statsMap[dayId];

        if (!dayTimes)
            return true;

        for (var time in dayTimes)
            if (dayTimes[time].info.num_trips > 0)
                return false;

        return true;
    };

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.tripCount = function(dayId, timeId) {
      var stats = getStats(dayId, timeId);
      if (!stats)
        return 0;

      return stats.info.num_trips;
    };

    function getStats(dayId, timeId) {
      dayId = dayId || 'all';
      timeId = timeId || 'all';
      return statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId] : null;
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    function loadStats(data) {
        $scope.times = [];
        var timesMap = {};

        for (var i in data) {
            var statGroup = data[i];
            var timeId = statGroup.info.hours == 'all' ? 'all' : statGroup.info.hours[0] + '-' + statGroup.info.hours[1];
            var dayId = statGroup.info.week_day;

            if (!statsMap[dayId])
                statsMap[dayId] = {};

            statsMap[dayId][timeId] = statGroup;

            if (timeId != 'all' && !timesMap[timeId]) {
                var time = {
                    id: timeId,
                    from: formatHour(statGroup.info.hours[0]),
                    to: formatHour(statGroup.info.hours[1])
                };
                timesMap[timeId] = time;
                $scope.times.push(time);
            }
        }

        function formatHour(hour) {
            return ('0' + hour % 24 + '').slice(-2) + ':00';
        }
    }
}]);
