angular.module('RouteExplorer').directive("timesDetails",
['env','Locale',
function(env) {
    return {
        restrict: 'E',
        scope: {
            stats: '='
        },
        controller: 'TimesDetailsController',
        templateUrl: env.baseDir + '/tpls/TimesDetails.html'
      };
}]);
