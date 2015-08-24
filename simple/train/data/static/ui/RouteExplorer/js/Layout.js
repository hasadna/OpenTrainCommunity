var app = angular.module('RouteExplorer');

app.factory('Layout', ['$http', '$q',
function($http, $q) {
    var stops = [];
    var stopsMap = {};
    var routes = [];
    var routesMap = {};

    var loaded = $q.all([
        $http.get('/api/stops')
            .then(function(response) {
                stops = response.data.map(function(s) { return { id: s.stop_id, name: s.heb_stop_names[0], names: s.heb_stop_names }; });
                stops.forEach(function(s) { stopsMap[s.id] = s; });
            }),

        $http.get('/api/all-routes')
            .then(function(response) {
                routes = response.data.map(function(r) { return {
                    id: r.id,
                    stops: r.stop_ids,
                    count: r.count
                }; });

                routesMap = routes.reduce(function(m, r) { m[r.id] = r; return m; }, {});
            })
    ]);

    var findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    var findRoutes = function(routes, originId, destinationId) {
        var matchingRoutes = {};

        routes.forEach(function(r) {
            var originIndex = r.stops.indexOf(originId);
            var destinationIndex = r.stops.indexOf(destinationId);

            if (originIndex < 0 || destinationIndex < 0)
                return;

            if (originIndex > destinationIndex)
                return;

            var routeStops = r.stops;
            var routeId = r.id;

            if (routeId in matchingRoutes)
                matchingRoutes[routeId].count += r.count;
            else {
                matchingRoutes[routeId] = {
                    id: routeId,
                    stops: routeStops,
                    count: r.count
                };
            }
        });

        matchingRoutes = Object.keys(matchingRoutes).map(function(routeId) { return matchingRoutes[routeId]; });
        matchingRoutes.sort(function(r1, r2) { return r2.count - r1.count; });
        return matchingRoutes;
    };

    var findRoutesByDate = function(origin, destination, year, month) {
        var d = $q.defer();
        var matchingRoutes = findRoutes(routes, origin, destination);
        if (matchingRoutes.length === 0) {
            d.resolve([]);
        } else {
            var fromDate = new Date(year, month - 1, 1);
            var toDate = new Date(year, month, 1);

            $http.get('/api/all-routes-by-date', {
                params: {
                    from_date: fromDate.getTime(),
                    to_date: toDate.getTime()
                }
            }).then(function(response) {
                var routesInDate = response.data.map(function(r) {
                    return {
                        id: r.id,
                        stops: r.stop_ids,
                        count: r.count
                    };
                });
                d.resolve(findRoutes(routesInDate, origin, destination));
            }, function(response) { d.reject({ 'msg': 'Error fetching routes', 'response': response }); });
        }

        return d.promise;
    };

    var findRoute = function(routeId) {
        return routesMap[routeId] || null;
    };

    return {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findRoute: findRoute,
        findStop: findStop,
        findRoutes: function(origin, destination) { return findRoutes(routes, origin, destination); },
        findRoutesByDate: findRoutesByDate,
        loaded: loaded
    };
}]);
