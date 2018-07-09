angular.module('RouteExplorer').directive("rexPercentBar",
['env',
function(env) {
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: env.baseDir + '/tpls/PercentBar.html'
      };
}]);
