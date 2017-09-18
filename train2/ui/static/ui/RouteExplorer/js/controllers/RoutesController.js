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
                console.log(result);
                return result;
            };
            $scope.init = () => {
                $scope.months = $scope.getMonths();
                $scope.years = $scope.getYears();
            };
            $scope.refresh = () => {

            }
            $scope.init();
        });






