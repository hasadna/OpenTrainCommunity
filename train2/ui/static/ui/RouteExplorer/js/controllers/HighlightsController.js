'use strict';

angular.module('RouteExplorer').controller('HighlightsController',
        function ($scope,
                  $http,
                  $q,
                  $timeout,
                  $location,
                  Layout,
                  daysTable,
                  hoursList,
                  monthNames) {
            'ngInject';
            $scope.init = () => {
                $http.get("/api/v1/highlights/").then(resp => {
                    $scope.highlights = resp.data;
                })
            }
            $scope.init();
        });






