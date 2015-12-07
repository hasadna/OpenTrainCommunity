(function() {
  var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap', 'ui.bootstrap.buttons']);

  app.constant('env', {
    baseDir: '/static/ui/RouteExplorer'
  });

  app.config(['$routeProvider', 'env',
  function($routeProvider, env) {

      var templateUrl = function(templateName) {
          return env.baseDir + '/tpls/' + templateName + '.html';
      };

      $routeProvider
          .when('/', {
              pageId: 'welcome',
              templateUrl: templateUrl('SelectStops'),
              controller: 'SelectStopsController',
              resolve: { 'Layout': 'Layout' }
          })
          .when('/about', {
              pageId: 'about',
              templateUrl: templateUrl('About')
          })
          .when('/:period/select-route/:origin/:destination', {
              pageId: 'routes',
              templateUrl: templateUrl('SelectRoute'),
              controller: 'SelectRouteController',
              resolve: { 'Layout': 'Layout' }
          })
          .when('/:period/routes/:routeId', {
              pageId: 'route',
              templateUrl: templateUrl('RouteDetails'),
              controller: 'RouteDetailsController',
              resolve: { 'Layout': 'Layout' },
              reloadOnSearch: false
          })
          .otherwise({
              redirectTo: '/'
          });
  }]);
})();
