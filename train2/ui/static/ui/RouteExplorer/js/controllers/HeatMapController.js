angular.module('RouteExplorer').controller('HeatMapController',
    ['$scope','$http', 'Layout', function($scope, $http, Layout) {
        $scope.Layout = Layout;
        var ta = $scope.Layout.findStop(4600);
        console.log(ta);
        angular.extend($scope, {
            defaults: {
                scrollWheelZoom: false
            },
            center: {
                lat: ta.latlon[0],
                lng: ta.latlon[1],
                zoom: 8,
            }
        });
        $http.get('/api/v1/heat-map/').then(function(resp) {
            $scope.heatmapData = resp.data;
            console.log($scope.heatmapData.length);
        });
}]);


