angular.module('RouteExplorer').factory('Layout',
['$http', '$q', 'TimeParser',
function($http, $q, TimeParser) {
    var self = this;
    var stops = [];
    var stopsMap = {};
    var routes = [];
    var routesMap = {};

    var loadedPromise = $q.all([
        $http.get('/api/v1/stops/')
            .then(function(response) {
                stops = response.data.map(function(s) { return {
                    id: s.stop_id,
                    name: s.heb_stop_names[0],
                    names: s.heb_stop_names,
                    latlon: s.latlon,
                }; });
                stops.forEach(function(s) { stopsMap[s.id] = s; });
            }),

        $http.get('/api/v1/routes/all/')
            .then(function(response) {
                routes = response.data.map(function(r) { return {
                    id: r.id,
                    stops: r.stop_ids,
                    count: r.count,
                    minDate: new Date(r.min_date),
                    maxDate: new Date(r.max_date)
                }; });

                routesMap = routes.reduce(function(m, r) { m[r.id] = r; return m; }, {});
            })
    ]);

    var findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    var findStopName = function(stopId) {
        return findStop(stopId).name;
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

    var findRoutesByPeriod = function(origin, destination, from, to) {
        // TODO use minDate and maxDate from our cached routes to avoid the http request

        var d = $q.defer();
        var matchingRoutes = findRoutes(routes, origin, destination);
        if (matchingRoutes.length === 0) {
            d.resolve([]);
        } else {
            var fromDate = from;
            var toDate = to;

            $http.get('/api/v1/routes/all-by-date/', {
                params: {
                    from_date: TimeParser.createRequestString(fromDate),
                    to_date: TimeParser.createRequestString(toDate)
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

    var getRoutesDateRange = function() {
        var max = new Date(1900, 0, 1);
        var min = new Date(2100, 0, 1);

        for (var i in routes) {
            var route = routes[i];
            if (route.count === 0)
              continue;

            if (route.minDate && route.minDate < min) min = route.minDate;
            if (route.maxDate && route.maxDate > max) max = route.maxDate;
        }
        return {
          min: min,
          max: max
        };
    };

    let service = {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findRoute: findRoute,
        findStop: findStop,
        findStopName: findStopName,
        findRoutes: function(origin, destination) { return findRoutes(routes, origin, destination); },
        findRoutesByPeriod: findRoutesByPeriod,
        getRoutesDateRange: getRoutesDateRange
    };

    return loadedPromise.then(function() { return service; });
}]);
