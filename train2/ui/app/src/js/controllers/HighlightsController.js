export default class HighlightsController {
    constructor($scope,
                $http,
                $q,
                $timeout,
                $location,
                Layout,
                ) {
        'ngInject';
        $scope.init = () => {
            $http.get("/api/v1/highlights/").then(resp => {
                $scope.highlights = resp.data.highlights;
                $scope.url = resp.data.url;
                $scope.fields = [
                    {
                        name: 'תאריך',
                        sortKey: v => {
                            return v.year * 100 + v.month;
                        }
                    },
                    {
                        name: 'מספר נסיעות',
                        sortKey: v => {
                            return v.num_trips;
                        },
                        initialDesc: true,
                    },
                    {
                        name: 'יום בשבוע',
                        sortKey: v => {
                            if (v.week_day == 'all') {
                                return -1;
                            }
                            return v.week_day;
                        }
                    },
                    {
                        name: 'שעות',
                        sortKey: v => {
                            if (v.hours == 'all') {
                                return -1;
                            }
                            return v.hours[1];
                        }
                    },
                    {
                        name: '% איחורים מעל 5 דקות',
                        active: true,
                        asc: false,
                        initialDesc: true,
                        sortKey: v => {
                            return v.mean_arrival_late_pct;
                        }
                    },
                    {
                        name: 'קישור',
                        disableSort: true,
                    }
                ];
                $scope.refresh();
            });

        };
        $scope.sortBy = function (activeField) {
            for (let f of $scope.fields) {
                if (f != activeField) {
                    f.active = false;
                }
            }
            if (activeField.active) {
                activeField.asc = !activeField.asc;
            } else {
                activeField.active = true;
                activeField.asc = !activeField.initialDesc;
            }
            $scope.refresh();
        };
        $scope.refresh = function () {
            let activeField = null;
            for (let f of $scope.fields) {
                if (f.active) {
                    activeField = f;
                }
            }
            if (!activeField) {
                return;
            }
            $scope.highlights.sort((v1, v2) => {
                let k1 = activeField.sortKey(v1);
                let k2 = activeField.sortKey(v2);
                let asc = activeField.asc ? 1 : -1;
                if (k1 > k2) {
                    return 1 * asc;
                }
                if (k1 < k2) {
                    return -1 * asc;
                }
                return 0;
            });
        };
        $scope.init();
    }
}






