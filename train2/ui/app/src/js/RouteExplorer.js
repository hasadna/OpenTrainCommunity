import angular from 'angular';
import 'angular-route';
import 'angular-ui-bootstrap';
import 'highcharts';
import 'highcharts-ng';

import AppController from "./controllers/AppController";
import SelectStopsController from "./controllers/SelectStopsController";
import SelectRouteController from "./controllers/SelectRouteController";
import RouteDetailsController from "./controllers/RouteDetailsController";
import GraphsController from "./controllers/GraphsController";
import TripDetailsController from "./controllers/TripDetails";
import HighlightsController from "./controllers/HighlightsController";

import RexPercentBar from "./directives/PercentBar"
import TimesDetails from "./directives/TimesDetails";

import Layout from "./services/Layout";
import Locale from "./services/Locale";
import LocationBinder from "./services/LocationBinder";
import TimeParser from "./services/TimeParser";

let app = angular.module('RouteExplorer', ['ngRoute',
    'ui.bootstrap',
    'ui.bootstrap.buttons',
    //'leaflet-directive',
    'highcharts-ng'
]);

app.config($locationProvider => {
});

app.controller('AppController', AppController)
    .controller('SelectStopsController', SelectStopsController)
    .controller('SelectRouteController', SelectRouteController)
    .controller('RouteDetailsController', RouteDetailsController)
    .controller('GraphsController', GraphsController)
    .controller('TripDetailsController', TripDetailsController)
    .controller('HighlightsController', HighlightsController)
;

app.directive('rexPercentBar', RexPercentBar);
app.directive('timesDetails', TimesDetails);

app.constant('env', {
    baseDir: '/static/ui'
});

app.factory('Layout', Layout)
    .factory('TimeParser', TimeParser)
    .factory('LocationBinder', LocationBinder)
    .constant('Locale', Locale);

app.config(['$routeProvider', 'env',
    function ($routeProvider, env) {
        let templateUrl = function (templateName) {
            return env.baseDir + '/tpls/' + templateName + '.html';
        };

        $routeProvider
            .when('/', {
                pageId: 'welcome',
                templateUrl: templateUrl('SelectStops'),
                controller: 'SelectStopsController',
                resolve: {'Layout': 'Layout'}
            })
            .when('/about', {
                pageId: 'about',
                templateUrl: templateUrl('About')
            })
            .when('/:period/select-route/:origin/:destination', {
                pageId: 'routes',
                templateUrl: templateUrl('SelectRoute'),
                controller: 'SelectRouteController',
                resolve: {'Layout': 'Layout'},
                reloadOnSearch: false
            })
            .when('/:period/routes/:routeId', {
                pageId: 'route',
                templateUrl: templateUrl('RouteDetails'),
                controller: 'RouteDetailsController',
                resolve: {'Layout': 'Layout'},
                reloadOnSearch: false
            }).when("/heat-map", {
            pageId: 'heatMap',
            templateUrl: templateUrl('HeatMap'),
            controller: 'HeatMapController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        }).when("/graphs", {
            pageId: 'graphs',
            templateUrl: templateUrl('Graphs'),
            controller: 'GraphsController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        })
        .when("/routes", {
            pageId: 'routes',
            templateUrl: templateUrl('RealRoutes'),
            controller: 'RealRoutesController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        })
        .when("/highlights", {
            pageId: 'highlights',
            templateUrl: templateUrl('Highlights'),
            controller: 'HighlightsController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        })
        .when("/top-highlights", {
            pageId: 'top_highlights',
            templateUrl: templateUrl('TopHighlights'),
            controller: 'TopHighlightsController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        })
        .when("/trip-details", {
            pageId: 'trip_details',
            templateUrl: templateUrl('TripDetails'),
            controller: 'TripDetailsController',
            reloadOnSearch: false,
            resolve: {'Layout': 'Layout'},
        })
        .otherwise({
            redirectTo: '/'
        });
    }]);

let daysTable = {
            0: 'ראשון',
            1: 'שני',
            2: 'שלישי',
            3: 'רביעי',
            4: 'חמישי',
            5: 'שישי',
            6: 'שבת',
        };

angular.module('RouteExplorer')
    .filter('week_day1', function () {
        return function (day) {
            if (day == 'all') {
                return 'כל הימים';
            }
            return daysTable[day-1] || `??? ${day}`;
        }
    }).filter('week_day0', function () {
        return function (day) {
            if (day == 'all') {
                return 'כל הימים';
            }
            return daysTable[day] || `??? ${day}`;
        }
    }).filter('hours', function () {
        return function(hours) {
            let fix = h => h >= 24 ? h % 24 : h;
            if (hours == 'all') {
                return 'כל היום'
            }
            let h1 = fix(hours[1]);
            let h0 = fix(hours[0]);
            return `${h1} - ${h0}`;
        }
    }).filter('month_name', function() {
        let months = [
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
        ]
        return function(m) {
            return months[m-1];
        }
    });


