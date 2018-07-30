function TimesDetailsController($scope, $route, Locale, LocationBinder, Layout) {
    'ngInject';
    $scope.layout = null;
    Layout.then(function(Layout) {
        $scope.layout = Layout;
    });
    let statsMap = {};
    let routeParams = $route.current.params;
    $scope.stopIds = [parseInt(routeParams.origin), parseInt(routeParams.destination)];
    console.log("In TimesDetailsController()");
    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');
    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    $scope.stopName = function(stopId) {
        if ($scope.layout) {
            var stop = $scope.layout.findStop(stopId);
            if (!stop)
                return null;

            return stop.name;
        } else {
            return null;
        }
    };

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

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.loadStats();
}


export default function TimesDetails(env, Layout) {
    'ngInject';
    return {
        restrict: 'E',
        scope: {
            stats: '='
        },
        controller: TimesDetailsController,
        templateUrl: env.baseDir + '/tpls/TimesDetails.html'
      };
};


