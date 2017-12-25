'use strict';
angular.module('RouteExplorer').controller('TripDetailsController',
        function ($scope,
                  $http,
                  $q,
                  $timeout,
                  $location,
                  Layout,
                  ) {
            'ngInject';
            $scope.isLegalTripId = () => {
                let n = $scope.tripId;
                return !isNaN(parseInt(n)) && !isNaN(n - 0)
            };
            $scope.refreshTrip = () => {
                $location.search({
                    'trip_id': $scope.tripId
                })
                $scope.wip = true;
                $http.get(`/api/1/data/trips/${tripId}/`).then(resp=> {
                    $scope.trip = resp.data;
                })
            }
        });






