var app = angular.module('FromTo', ['my.filters','my.services','my.directives']);

app.controller('FromToController', ['$scope', 'MyHttp',
function($scope, MyHttp) {
    $scope.stops = [];
    $scope.input = {
        fromStop : null,
        toStop : null,
    };
    $scope.results = null;
    MyHttp.get('/api/stops').success(function(data) {
        $scope.stops = data;
        $scope.input.fromStop = $scope.stops[0];
        $scope.input.toStop = $scope.stops[0];
        $scope.input.fromHour = localStorage.fromHour || null;
        $scope.input.toHour = localStorage.toHour || null;
        if (localStorage.fromStop || localStorage.toStop) {
            $scope.stops.forEach(function(stop) {
                if (stop.stop_id == localStorage.fromStop) {
                    $scope.input.fromStop = stop;
                };
                if (stop.stop_id == localStorage.toStop) {
                    $scope.input.toStop = stop;
                }
            });
        }
    });
    $scope.go = function() {
        $scope.results = null;
        localStorage.setItem('fromStop',$scope.input.fromStop.stop_id);
        localStorage.setItem('toStop',$scope.input.toStop.stop_id);
        localStorage.setItem('fromHour',$scope.input.fromHour);
        localStorage.setItem('toHour',$scope.input.toHour);
        MyHttp.get('/api/routes/',
            {'from' : $scope.input.fromStop.stop_id,
            'to' : $scope.input.toStop.stop_id,
            'from_time' : $scope.input.fromHour,
            'to_time' : $scope.input.toHour
            }).success(function(data) {
               if ( data.total ) {
                    $scope.results = data;
                } else {
                    $scope.results = null;
                }
                console.log('results = ' + $scope.results);
            });
    };
}]);

