var baseDir = '/static/ui/RouteExplorer';
var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap', 'ui.bootstrap.buttons']);

app.config(['$routeProvider',
function($routeProvider) {

    var templateUrl = function(templateName) {
        return baseDir + '/tpls/' + templateName + '.html';
    };

    $routeProvider
        .when('/', {
            templateUrl: templateUrl('SelectStops'),
            controller: 'SelectStopsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .when('/select-route/:origin/:destination', {
            templateUrl: templateUrl('SelectRoute'),
            controller: 'SelectRouteController',
            resolve: {
                loaded: function(Layout) {
                return Layout.loaded;
                }
            }
        })
        .when('/route-details/:stop_ids', {
            templateUrl: templateUrl('RouteDetails'),
            controller: 'RouteDetailsController',
            resolve: {
                loaded: function(Layout) {
                    return Layout.loaded;
                }
            }
        })
        .otherwise({
            redirectTo: '/'
        });
}]);


app.controller('SelectStopsController', ['$scope', '$location', 'Layout',
function($scope, $location, Layout) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;

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

        return stop.shortName;
    };

    $scope.goToRoutes = function() {
        $location.path('/select-route/' + $scope.origin.id + '/' + $scope.destination.id)
    }
}]);

app.controller('SelectRouteController', ['$scope', '$location', '$route', 'Layout',
function($scope, $location, $route, Layout) {
    $scope.stops = Layout.getStops();
    var origin = Layout.findStop($route.current.params['origin']);
    var destination = Layout.findStop($route.current.params['destination']);
    $scope.routes = Layout.findRoutes(origin.id, destination.id);

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.shortName;
    };

    $scope.barWidth = function(route) {
        var percentWidth = route.count * 100.0 / $scope.routes[0].count;

        if (percentWidth < 1.0)
            return "1px";

        return percentWidth + "%";
    };

    $scope.goToRouteDetails = function(route) {
        $location.path('/route-details/' + route.stops.join(','));
    };
}]);

app.controller('RouteDetailsController', ['$scope', '$route', '$http', 'Layout',
function($scope, $route, $http, Layout) {
    var stopList = $route.current.params['stop_ids'];
    var stopIds = stopList.split(',');

    $scope.loaded = false;

    $http.get('/api/path-info', { params: { stop_ids: stopList } })
        .success(function(data) {
            $scope.stats = data;
            $scope.loaded = true;
        });

    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];

    $scope.selectedDay = null;
    $scope.days = [
        { abbr: 'א', title: 'ראשון', value: 1 },
        { abbr: 'ב', title: 'שני', value: 2 },
        { abbr: 'ג', title: 'שלישי', value: 3 },
        { abbr: 'ד', title: 'רביעי', value: 4 },
        { abbr: 'ה', title: 'חמישי', value: 5 },
        { abbr: 'ו', title: 'שישי', value: 6 },
        { abbr: 'ש', title: 'שבת', value: 7 }
    ];

    $scope.selectedTime = null;
    $scope.times = [
        { from: '07:00', to: '09:00' },
        { from: '09:00', to: '12:00' },
        { from: '12:00', to: '16:00' },
        { from: '16:00', to: '18:00' },
        { from: '18:00', to: '20:00' },
        { from: '20:00', to: '22:00' },
        { from: '22:00', to: '00:00' }
    ];

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

            return stop.shortName;
    }
}]);

app.filter('duration', function() {
    return function(seconds) {
        var negative = false;
        seconds = Math.trunc(seconds);
        if (seconds < 0) {
            negative = true;
            seconds = -seconds;
        }

        var minutes = Math.trunc(seconds / 60);
        seconds -= minutes * 60;
        var hours = Math.trunc(minutes / 60);
        minutes -= hours * 60;

        if (seconds < 10) seconds = '0' + seconds;
        if (minutes < 10 && hours != 0) minutes = '0' + minutes;

        var res = minutes + ':' + seconds;
        if (hours != 0)
            res = hours + ':' + res;

        if (negative)
            res = '-' + res;

        return res;
    }
});

app.directive("rexPercentBar", function() {
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: baseDir + '/tpls/PercentBar.html'
      };
});
