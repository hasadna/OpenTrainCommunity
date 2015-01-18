var app = angular.module('RouteExplorer');

app.factory('Layout', ['$http', '$q',
function($http, $q) {
    var stops = [];
    var stopsMap = {};
    var routes = [];

    var loaded = $q.all([
        $http.get('/api/stops')
            .success(function(data) {
                stops = data.map(function(s) { return { id: s.stop_id, name: s.stop_name, shortName: s.stop_short_name }; });
                stops.forEach(function(s) { stopsMap[s.id] = s; });
            }),

        $http.get('/api/all-routes')
            .success(function(data) {
                routes = data.map(function(r) { return {
                    stops: r.stops.map(function(s) { return s.stop_id; }),
                    count: r.count
                }});
            })
    ]);

    var findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    var findPaths = function(originId, destinationId) {
        var paths = {};

        routes.forEach(function(r) {
            var originIndex = r.stops.indexOf(originId);
            var destinationIndex = r.stops.indexOf(destinationId);

            if (originIndex < 0 || destinationIndex < 0)
                return;

            if (originIndex > destinationIndex)
                return;

            var pathStops = r.stops.slice(originIndex, destinationIndex + 1);
            var pathId = pathStops.join(',');

            if (pathId in paths)
                paths[pathId].count += r.count;
            else {
                paths[pathId] = {
                    stops: pathStops,
                    count: r.count
                };
            }
        });

        paths = Object.keys(paths).map(function(pathId) { return paths[pathId] });
        paths.sort(function(p1, p2) { return p2.count - p1.count; });
        return paths;
    };

    return {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findStop: findStop,
        findPaths: findPaths,
        loaded: loaded
    }
}]);
