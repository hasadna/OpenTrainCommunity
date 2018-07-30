import {TimeParser} from "../lib/dt_lib";

export default function Layout($http, $q) {
    'ngInject';
    let stops = [];
    let stopsMap = {};
    let routes = [];
    let routesMap = {};

    let loadedPromise = $q.all([
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

    let findStop = function(stopId) {
        return stopsMap[stopId] || null;
    };

    let findStopName = function(stopId) {
        return findStop(stopId).name;
    };

    let findRoutes = function(routes, originId, destinationId) {
        let matchingRoutes = {};

        routes.forEach(function(r) {
            let originIndex = r.stops.indexOf(originId);
            let destinationIndex = r.stops.indexOf(destinationId);

            if (originIndex < 0 || destinationIndex < 0)
                return;

            if (originIndex > destinationIndex)
                return;

            let routeStops = r.stops;
            let routeId = r.id;

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

    let findRoutesByPeriod = function(origin, destination, from, to) {
        // TODO use minDate and maxDate from our cached routes to avoid the http request

        let d = $q.defer();
        let matchingRoutes = findRoutes(routes, origin, destination);
        if (matchingRoutes.length === 0) {
            d.resolve([]);
        } else {
            let fromDate = from;
            let toDate = to;

            $http.get('/api/v1/routes/all-by-date/', {
                params: {
                    from_date: TimeParser.createRequestString(fromDate),
                    to_date: TimeParser.createRequestString(toDate)
                }
            }).then(function(response) {
                let routesInDate = response.data.map(function(r) {
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

    let findRoute = function(routeId) {
        return routesMap[routeId] || null;
    };

    let getRoutesDateRange = function() {
        let max = new Date(1900, 0, 1);
        let min = new Date(2100, 0, 1);

        for (let i in routes) {
            let route = routes[i];
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
    return loadedPromise.then(() => {
        // console.log("promise resolved...");
        return service;
    });
};
