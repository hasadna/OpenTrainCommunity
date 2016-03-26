angular.module('RouteExplorer').controller('AppController',
['$scope', '$location',
function($scope, $location) {
    $scope.share = function(prefix) {
        var url = prefix + encodeURIComponent('http://otrain.org/#' + $location.url());
        window.open(url, 'sharePopup', 'width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no');
    };

    $scope.$on('$routeChangeSuccess', function(e, route) {
        $scope.bodyClass = route.pageId ? 'rex-page-' + route.pageId : null;
    });
}]);
