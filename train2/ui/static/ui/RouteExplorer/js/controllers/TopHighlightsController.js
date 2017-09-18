'use strict';

angular.module('RouteExplorer').controller('TopHighlightsController',
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
                $http.get("/api/v1/highlights/top/").then(resp => {
                    let data = resp.data.highlights;
                    $scope.highlightLists =  [
                        {
                            'kind': 'late',
                            'title': 'נסיעה באיחור',
                            'items': data.late,
                        },
                        {
                            'kind': 'ontime',
                            'title': 'נסיעה בזמן',
                            'items': data.ontime,
                        }
                    ];
                });
            };
            $scope.init();
        });






