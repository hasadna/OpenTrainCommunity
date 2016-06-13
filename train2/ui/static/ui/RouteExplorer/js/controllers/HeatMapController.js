angular.module('RouteExplorer').controller('HeatMapController',
    ['$scope', '$http', 'Layout', function ($scope, $http, Layout) {
        $scope.Layout = Layout;
        var ta = $scope.Layout.findStop(4600); // TA HASHALOM
        console.log(ta);
        angular.extend($scope, {
            defaults: {
                scrollWheelZoom: false
            },
            center: {
                lat: ta.latlon[0],
                lng: ta.latlon[1],
                zoom: 10,
            }
        });
        $scope.paths = [];
        $http.get('/api/v1/heat-map/').then(function (resp) {
            $scope.heatmapData = resp.data;
            //var maxScore = 0;
            //var minScore = 1;

            //$scope.heatmapData.forEach(function(score) {
            //    maxScore = Math.max(score.score, maxScore);
            //    minScore = Math.min(score.score, minScore);
            //});

            $scope.heatmapData.forEach(function (score) {
                var latlng = $scope.Layout.findStop(score.stop_id).latlon;
                var g = 255-Math.floor(255 * score.score);
                var color = 'rgb(255,' + g + ',0)';
                $scope.paths.push({
                    color: color,
                    fillColor: color,
                    fillOpacity: 1,
                    type: "circleMarker",
                    stroke: false,
                    radius: 10,
                    latlngs: latlng
                });
            });
        });

    }]);


