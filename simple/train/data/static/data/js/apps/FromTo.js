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
        var oldInput = JSON.parse(localStorage.getItem('input'));
        $scope.input.fromStop = $scope.stops[0];
        $scope.input.toStop = $scope.stops[0];
        $scope.input.fromHour = null;
        $scope.input.toHour = null;
        $scope.input.days = [true,true,true,true,true,true,true];
        if (oldInput) {
            $scope.stops.forEach(function(stop) {
                if (oldInput.fromStop && stop.stop_id == oldInput.fromStop.stop_id) {
                    $scope.input.fromStop = stop;
                };
                if (oldInput.toStop && stop.stop_id == oldInput.toStop.stop_id) {
                    $scope.input.toStop = stop;
                }
            });
            $scope.input.days = oldInput.days;
            $scope.input.fromHour = oldInput.fromHour;
            $scope.input.toHour = oldInput.toHour;
        }
    });
    $scope.go = function() {
        $scope.results = null;
        localStorage.setItem('input',JSON.stringify($scope.input));
        var positive = [];
        for (var i = 0 ; i < 7 ; i++ ) {
            if ($scope.input.days[i]) {
                positive.push(i);
            }
        };
        MyHttp.get('/api/routes/',
            {from : $scope.input.fromStop.stop_id,
            to : $scope.input.toStop.stop_id,
            from_time : $scope.input.fromHour,
            to_time : $scope.input.toHour,
            days : positive.join(','),
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

