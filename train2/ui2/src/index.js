import 'angular';
import 'angular-route';

import SelectStopsController from 'pages/select-stops/ctrl.js';

let app = angular.module('RouteExplorer', [
    'ngRoute',
]);

app.config(['$routeProvider','env',
    function ($routeProvider, env) {

        var templateUrl = templateName => env.baseDir + '/tpls/' + templateName + '.html';

        $routeProvider
            .when('/', {
                pageId: 'welcome',
                templateUrl: templateUrl('SelectStops'),
                controller: 'SelectStopsController',
                resolve: {'Layout': 'Layout'}
            })
            // .when('/about', {
            //     pageId: 'about',
            //     templateUrl: templateUrl('About')
            // })
            // .when('/:period/select-route/:origin/:destination', {
            //     pageId: 'routes',
            //     templateUrl: templateUrl('SelectRoute'),
            //     controller: 'SelectRouteController',
            //     resolve: {'Layout': 'Layout'},
            //     reloadOnSearch: false
            // })
            // .when('/:period/routes/:routeId', {
            //     pageId: 'route',
            //     templateUrl: templateUrl('RouteDetails'),
            //     controller: 'RouteDetailsController',
            //     resolve: {'Layout': 'Layout'},
            //     reloadOnSearch: false
            // }).when("/heat-map", {
            //     pageId: 'heatMap',
            //     templateUrl: templateUrl('HeatMap'),
            //     controller: 'HeatMapController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // }).when("/graphs", {
            //     pageId: 'graphs',
            //     templateUrl: templateUrl('Graphs'),
            //     controller: 'GraphsController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // })
            // .when("/routes", {
            //     pageId: 'routes',
            //     templateUrl: templateUrl('RealRoutes'),
            //     controller: 'RealRoutesController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // })
            // .when("/highlights", {
            //     pageId: 'highlights',
            //     templateUrl: templateUrl('Highlights'),
            //     controller: 'HighlightsController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // })
            // .when("/top-highlights", {
            //     pageId: 'top_highlights',
            //     templateUrl: templateUrl('TopHighlights'),
            //     controller: 'TopHighlightsController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // })
            // .when("/trip-details", {
            //     pageId: 'trip_details',
            //     templateUrl: templateUrl('TripDetails'),
            //     controller: 'TripDetailsController',
            //     reloadOnSearch: false,
            //     resolve: {'Layout': 'Layout'},
            // })
            .otherwise({
                redirectTo: '/'
            });
    }]);
