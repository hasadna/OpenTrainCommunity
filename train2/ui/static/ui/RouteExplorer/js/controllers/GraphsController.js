'use strict';
angular.module('RouteExplorer').controller('GraphsController',
    ['$scope', '$http', '$q', 'Layout', function ($scope, $http, $q, Layout) {
        $scope.Layout = Layout;
        $scope.input = {

        };
        $scope.refresh = function() {
            var routeId = $scope.input.selectedRoute.id;
            $scope.routeId =  routeId;
            $scope.startDate = $scope.input.startDate.value;
            $scope.endDate = $scope.input.endDate.value;
            $scope.stops = Layout.getStops();
            var cbs = [
                $http.get('/api/v1/stats/route-info-full/', {
                    params: {
                        from_date: $scope.startDate,
                        to_date: $scope.endDate,
                        route_id: $scope.routeId,
                    }
                }).then(function(resp) {
                    $scope.stat = resp.data;
                }),
                $http.get('/api/v1/routes/' + $scope.routeId + '/').then(function(resp) {
                    $scope.route = resp.data;
                }),
            ];
            $q.all(cbs).then(function() {
                console.log('done');
            });
        };
        $scope.getRouteTitle = function(route) {
            return  'מ' + route.from + ' ל' + route.to + ' (' + route.count + ' ' + 'נסיעות' + ')';
        }

        $scope.initData = function() {
            $scope.buildDates();
            return $scope.buildRoutes();
        };

        $scope.buildRoutes = function() {
            return $http.get('/api/v1/routes/all/').then(function(resp) {
                var routes = resp.data;
                var sortedRoutes = routes.map(function (r) {
                    return {
                        id: r.id,
                        from: Layout.findStopName(r.stop_ids[0]),
                        to: Layout.findStopName(r.stop_ids[r.stop_ids.length - 1]),
                        count: r.count
                    }
                });
                sortedRoutes.sort(function (s1, s2) {
                    if (s1.from < s2.from) {
                        return -1;
                    }
                    if (s1.from > s2.from) {
                        return 1;
                    }
                    if (s1.to < s2.to) {
                        return -1;
                    }
                    if (s1.to > s2.to) {
                        return 1;
                    }
                    if (s1.count > s2.count) {
                        return -1; // reverse count
                    }
                    if (s1.count < s2.count) {
                        return 1; //reverse count
                    }
                    return 0;
                });
                $scope.routes = sortedRoutes;
            });
        };
        $scope.buildDates = function() {
            var monthNames = [
                'dummy',
                'ינואר',
                'פברואר',
                'מרץ',
                'אפריל',
                'מאי',
                'יוני',
                'יולי',
                'אוגוסט',
                'ספטמבר',
                'אוקטובר',
                'נובמבר',
                'דצמבר'
            ];
            var s = [1, 2015];
            var e = [4, 2016];
            $scope.startDates = [];
            $scope.endDates = [];
            while (s[0] != e[0] || s[1] != e[1]) {
                $scope.startDates.push({
                    name: monthNames[s[0]] + ' ' + s[1],
                    value: '1/' + s[0] + '/' + s[1],
                });
                var ns = s[0] == 12 ? [1,s[1] + 1] : [s[0] + 1, s[1]];
                $scope.endDates.push({
                    name: monthNames[s[0]] + ' ' + s[1],
                    value: '1/' + ns[0]  + '/' + ns[1],
                });
                s[0] = s[0] + 1;
                if (s[0] > 12) {
                    s[0] = 1;
                    s[1]++;
                }
            }
        };
        $scope.findRoute = function(rid) {
            for (var i = 0 ; i < $scope.routes.length ; i++ ) {
                if ($scope.routes[i].id == rid) {
                    return $scope.routes[i];
                }
            }
            throw "could not find route (from " + $scope.routes.length + ") with id = " + rid;
        }
        $scope.initData().then(function() {
            $scope.input.startDate = $scope.startDates[10];
            $scope.input.endDate = $scope.endDates[11];
            $scope.input.selectedRoute = $scope.findRoute(10);
            $scope.refresh();
        });
    }]);




