'use strict';

angular.module('RouteExplorer').controller('RealRoutesController',
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
            $scope.selectedYear = 2017;
            $scope.selectedMonth = 9;
            $scope.getMonths = () => {
                return [1,2,3,4,5,6,7,8,9,10,11,12];
            };
            $scope.getYears = () => {
                let result = [];
                let lastYear = new Date().getFullYear();
                let y = 2015;
                while (y <= lastYear) {
                    result.push(y);
                    y++;
                }
                return result;
            };
            $scope.init = () => {
                $scope.months = $scope.getMonths();
                $scope.years = $scope.getYears();
            };
            $scope.refresh = () => {
                $scope.realRoutes = null;
                let y = $scope.selectedYear;
                let m = $scope.selectedMonth;
                $http.get(`/api/v1/real-routes/${y}/${m}/`).then(resp => {
                    $scope.realRoutes = resp.data;
                    for (let rr of $scope.realRoutes) {
                        console.log(rr);
                        rr.firstStop = rr.stops[0];
                        rr.lastStop = rr.stops[rr.stops.length-1];
                    }
                });
            }
            $scope.init();
        });






