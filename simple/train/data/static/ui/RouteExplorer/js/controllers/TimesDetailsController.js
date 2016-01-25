angular.module('RouteExplorer').controller('TimesDetailsController',
    ['$scope', '$route', 'Locale','LocationBinder',
function($scope, $route, Locale, LocationBinder) {
    var statsMap = {};
    var routeParams = $route.current.params;
    console.log(routeParams);
    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');
    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }
    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    $scope.loadStats = function() {
        var data = $scope.stats;
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
    $scope.loadStats();
}]);

