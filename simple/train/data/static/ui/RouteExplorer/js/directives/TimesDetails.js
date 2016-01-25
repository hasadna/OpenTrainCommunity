angular.module('RouteExplorer').directive("timesDetails",
['env','Layout',
function(env, Layout) {
    return {
        restrict: 'E',
        scope: {
            stats: '='
        },
        controller: 'TimesDetailsController',
        templateUrl: env.baseDir + '/tpls/TimesDetails.html'
      };
}]);
