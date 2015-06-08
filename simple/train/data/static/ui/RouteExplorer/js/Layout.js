var app = angular.module('RouteExplorer');

app.factory('Layout', ['$http', '$q',
function($http, $q) {
    var stops = [];
    var stopsMap = {};
    var routes = [];

    var loaded = $q.all([
        $http.get('/api/stops')
            .success(function(data) {
                stops = data.map(function(s) { return { id: s.stop_id, name: s.heb_stop_names[0], names: s.heb_stop_names }; });
                stops.forEach(function(s) { stopsMap[s.id] = s; });
            }),

        $http.get('/api/all-routes')
            .success(function(data) {
                routes = data.map(function(r) { return {
                    stops: r.stop_ids,
                    count: r.count
                }; });
            })
    ]);

    var findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    var findRoutes = function(originId, destinationId) {
        var matchingRoutes = {};

        routes.forEach(function(r) {
            var originIndex = r.stops.indexOf(originId);
            var destinationIndex = r.stops.indexOf(destinationId);

            if (originIndex < 0 || destinationIndex < 0)
                return;

            if (originIndex > destinationIndex)
                return;

            var routeStops = r.stops;
            var routeId = routeStops.join(',');

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

    return {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findStop: findStop,
        findRoutes: findRoutes,
        loaded: loaded
    };
}]);
