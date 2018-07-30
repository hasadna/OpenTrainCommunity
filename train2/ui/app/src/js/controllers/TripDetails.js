export default class TripDetailsController {
    constructor($scope,
                $http,
                $q,
                $timeout,
                $location,
                Layout,
    ) {``
        'ngInject';
        $scope.isLegalTripId = () => {
            let n = $scope.tripId;
            return true;
            return !isNaN(parseInt(n)) && !isNaN(n - 0)
        };
        $scope.x_fields = [
            "x_week_day_local",
            "x_hour_local",
            "x_max_delay_arrival",
            "x_max2_delay_arrival",
            "x_avg_delay_arrival",
            "x_last_delay_arrival",
            "x_before_last_delay_arrival"
        ]

        $scope.refreshTrip = () => {
            $location.search({
                'trip_id': $scope.tripId
            })
            $scope.wip = true;
            $scope.getError = false;
            $scope.trip = null;
            $http.get(`/api/v1/trips/${$scope.tripId}/`).then(resp => {
                $scope.trip = resp.data;
                $scope.wip = false;
            }, resp => {
                $scope.wip = false;
                $scope.getError = true;
            })
        }
        $scope.tripId = parseInt($location.search().trip_id) || null;
        if ($scope.tripId) {
            $scope.refreshTrip();
        }
    }
}





