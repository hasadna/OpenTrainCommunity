<<<<<<< HEAD
!function(){var t=angular.module("RouteExplorer",["ngRoute","ui.bootstrap","ui.bootstrap.buttons"]);t.constant("env",{baseDir:"/static/ui/RouteExplorer"}),t.config(["$routeProvider","env",function(t,e){var n=function(t){return e.baseDir+"/tpls/"+t+".html"};t.when("/",{pageId:"welcome",templateUrl:n("SelectStops"),controller:"SelectStopsController",resolve:{Layout:"Layout"}}).when("/about",{pageId:"about",templateUrl:n("About")}).when("/:period/select-route/:origin/:destination",{pageId:"routes",templateUrl:n("SelectRoute"),controller:"SelectRouteController",resolve:{Layout:"Layout"}}).when("/:period/routes/:routeId",{pageId:"route",templateUrl:n("RouteDetails"),controller:"RouteDetailsController",resolve:{Layout:"Layout"},reloadOnSearch:!1}).otherwise({redirectTo:"/"})}])}(),String.prototype.repeat||(String.prototype.repeat=function(t){"use strict";if(null===this)throw new TypeError("can't convert "+this+" to object");var e=""+this;if(t=+t,t!=t&&(t=0),0>t)throw new RangeError("repeat count must be non-negative");if(t==1/0)throw new RangeError("repeat count must be less than infinity");if(t=Math.floor(t),0===e.length||0===t)return"";if(e.length*t>=1<<28)throw new RangeError("repeat count must not overflow maximum string size");for(var n="";1==(1&t)&&(n+=e),t>>>=1,0!==t;)e+=e;return n}),angular.module("RouteExplorer").controller("AppController",["$scope","$location",function(t,e){t.share=function(t){var n=t+encodeURIComponent("http://otrain.org/#"+e.url());window.open(n,"sharePopup","width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no")},t.$on("$routeChangeSuccess",function(e,n){t.bodyClass=n.pageId?"rex-page-"+n.pageId:null})}]),angular.module("RouteExplorer").controller("RouteDetailsController",["$scope","$route","$http","$location","LocationBinder","Layout","Locale","TimeParser",function(t,e,n,r,o,i,u,a){function l(t,e){return t=t||"all",e=e||"all",y[t]&&y[t][e]?y[t][e]:null}function s(){var e=l(t.selectedDay,t.selectedTime);return e?e.stops:[]}function c(e){function n(t){return("0"+t%24).slice(-2)+":00"}t.times=[];var r={};for(var o in e){var i=e[o],u="all"==i.info.hours?"all":i.info.hours[0]+"-"+i.info.hours[1],a=i.info.week_day;if(y[a]||(y[a]={}),y[a][u]=i,"all"!=u&&!r[u]){var l={id:u,from:n(i.info.hours[0]),to:n(i.info.hours[1])};r[u]=l,t.times.push(l)}}}function d(t){return u.months[t.getMonth()].name+" "+t.getFullYear()}function f(t,e){var n=new Date(t);return n.setMonth(n.getMonth()+e),n}function p(t,e){return size=12*(t.to.getFullYear()-t.from.getFullYear())+t.to.getMonth()-t.from.getMonth()+1,{from:f(t.from,size*e),to:f(t.to,size*e),end:f(t.end,size*e)}}var m=e.current.params,g=a.parsePeriod(m.period),h=g.from,v=g.end,b=m.routeId,R=i.findRoute(b).stops,y={};t.loaded=!1,t.stopIds=R,t.origin=R[0],t.destination=R[R.length-1],t.selectedPeriod=d(g.from),g.to>g.from&&(t.selectedPeriod+=" — "+d(g.to)),t.selectedDay=null,t.days=u.days,t.selectedTime=null,t.times=[],t.selectRouteUrl="#/"+m.period+"/select-route/"+t.origin+"/"+t.destination;var D=p(g,-1),w=p(g,1),P=i.getRoutesDateRange();t.previousPeriodUrl=P.min<D.from?"#/"+a.formatPeriod(D)+"/routes/"+b:null,t.nextPeriodUrl=P.max>w.to?"#/"+a.formatPeriod(w)+"/routes/"+b:null,n.get("/api/route-info-full",{params:{route_id:b,from_date:h.getTime(),to_date:v.getTime()}}).success(function(e){c(e),t.loaded=!0}),o.bind(t,"selectedDay","day",function(t){return t?Number(t):null}),o.bind(t,"selectedTime","time"),t.stopStats=function(t){var e=s();for(var n in e)if(e[n].stop_id==t)return e[n];return null},t.stopName=function(t){var e=i.findStop(t);return e?e.name:null},t.isDayEmpty=function(t){var e=t.id,n=y[e];if(!n)return!0;for(var r in n)if(n[r].info.num_trips>0)return!1;return!0},t.isTimeEmpty=function(e){var n=t.selectedDay||"all",r=e.id,o=y[n]&&y[n][r];return o&&o.info.num_trips>0?!1:!0},t.tripCount=function(t,e){var n=l(t,e);return n?n.info.num_trips:0}}]),angular.module("RouteExplorer").controller("SelectRouteController",["$scope","$location","$route","Layout","TimeParser",function(t,e,n,r,o){function i(t){var e=r.findStop(t);return e?e.name:null}function u(t){function e(t){var e={};for(var n in t){var r=t[n];for(var o in r.stops){var i=r.stops[o];e[i]||(e[i]=0),e[i]++}}return e}function n(t,e){var n={};for(var r in t)t[r]==e&&(n[r]=!0);return n}function r(t,e){var n,r=[];for(var o in t){var i=t[o];o>0&&o<t.length-1&&e[i]?(n||(n=[],r.push(n)),n.push(i)):(n=null,r.push(i))}return r}var o=n(e(t),t.length);delete o[l.id],delete o[s.id];for(var i in t)t[i].stops=r(t[i].stops,o)}t.stops=r.getStops();var a=o.parsePeriod(n.current.params.period),l=r.findStop(n.current.params.origin),s=r.findStop(n.current.params.destination);r.findRoutesByPeriod(l.id,s.id,a.from,a.end).then(function(e){e.length>1&&u(e),t.routes=e}),t.isCollapsed=function(t){return angular.isArray(t)},t.isOrigin=function(t){return t==l.id},t.isDestination=function(t){return t==s.id},t.stopText=function(e){return t.isCollapsed(e)?"•".repeat(e.length):i(e)},t.stopTooltip=function(e){return t.isCollapsed(e)?e.map(i).join(", "):null},t.barWidth=function(e){var n=100*e.count/t.routes[0].count;return 1>n?"1px":n+"%"},t.routeUrl=function(t){return"/#/"+n.current.params.period+"/routes/"+t.id}}]),angular.module("RouteExplorer").controller("SelectStopsController",["$scope","$rootScope","$location","Layout","Locale","TimeParser",function(t,e,n,r,o,i){function u(t,e){t.getFullYear()<2013&&(t=new Date(2013,0,1));for(var n=[],r=new Date(t.getFullYear(),t.getMonth(),1);e>r;){end=new Date(r.getFullYear(),r.getMonth()+1,r.getDate());var i={from:r,to:r,end:end,name:o.months[r.getMonth()].name+" "+r.getFullYear()};i.toName=o.until+i.name,n.push(i),r=end}return n.reverse(),n}t.stops=r.getStops(),t.origin=null,t.destination=null,t.months=o.months;var a=r.getRoutesDateRange();t.periods=u(a.min,a.max),t.startPeriod=t.periods[0],t.endPeriod=t.periods[0],t.formValid=function(){return!!t.origin&&!!t.destination&&t.origin!=t.destination&&t.startPeriod.from<=t.endPeriod.to},t.stopName=function(t){var e=r.findStop(t);return e?e.name:null},t.goToRoutes=function(){t.noRoutes=!1,t.loading=!0;var e={from:t.startPeriod.from,to:t.endPeriod.to,end:t.endPeriod.end},o=e.from,u=e.end,a=i.formatPeriod(e);r.findRoutesByPeriod(t.origin.id,t.destination.id,o,u).then(function(e){0===e.length?t.noRoutes=!0:1==e.length?n.path("/"+a+"/routes/"+e[0].id):n.path("/"+a+"/select-route/"+t.origin.id+"/"+t.destination.id)})["finally"](function(){t.loading=!1})},t.dismissError=function(){t.noRoutes=!1}}]),angular.module("RouteExplorer").directive("rexPercentBar",["env",function(t){return{restrict:"E",scope:{value:"=value",type:"=type"},templateUrl:t.baseDir+"/tpls/PercentBar.html"}}]),angular.module("RouteExplorer").filter("duration",function(){return function(t){var e=!1;t=Math.trunc(t),0>t&&(e=!0,t=-t);var n=Math.trunc(t/60);t-=60*n;var r=Math.trunc(n/60);n-=60*r,10>t&&(t="0"+t),10>n&&0!==r&&(n="0"+n);var o=n+":"+t;return 0!==r&&(o=r+":"+o),e&&(o="-"+o),o}}),angular.module("RouteExplorer").factory("Layout",["$http","$q",function(t,e){var n=[],r={},o=[],i={},u=e.all([t.get("/api/stops").then(function(t){n=t.data.map(function(t){return{id:t.stop_id,name:t.heb_stop_names[0],names:t.heb_stop_names}}),n.forEach(function(t){r[t.id]=t})}),t.get("/api/all-routes").then(function(t){o=t.data.map(function(t){return{id:t.id,stops:t.stop_ids,count:t.count,minDate:new Date(t.min_date),maxDate:new Date(t.max_date)}}),i=o.reduce(function(t,e){return t[e.id]=e,t},{})})]),a=function(t){return r[t]||null},l=function(t,e,n){var r={};return t.forEach(function(t){var o=t.stops.indexOf(e),i=t.stops.indexOf(n);if(!(0>o||0>i||o>i)){var u=t.stops,a=t.id;a in r?r[a].count+=t.count:r[a]={id:a,stops:u,count:t.count}}}),r=Object.keys(r).map(function(t){return r[t]}),r.sort(function(t,e){return e.count-t.count}),r},s=function(n,r,i,u){var a=e.defer(),s=l(o,n,r);if(0===s.length)a.resolve([]);else{var c=i,d=u;t.get("/api/all-routes-by-date",{params:{from_date:c.getTime(),to_date:d.getTime()}}).then(function(t){var e=t.data.map(function(t){return{id:t.id,stops:t.stop_ids,count:t.count}});a.resolve(l(e,n,r))},function(t){a.reject({msg:"Error fetching routes",response:t})})}return a.promise},c=function(t){return i[t]||null},d=function(){var t=new Date(1900,0,1),e=new Date(2100,0,1);for(var n in o)route=o[n],0!==route.count&&(route.minDate&&route.minDate<e&&(e=route.minDate),route.maxDate&&route.maxDate>t&&(t=route.maxDate));return{min:e,max:t}};return service={getStops:function(){return n},getRoutes:function(){return o},findRoute:c,findStop:a,findRoutes:function(t,e){return l(o,t,e)},findRoutesByPeriod:s,getRoutesDateRange:d},u.then(function(){return service})}]),angular.module("RouteExplorer").constant("Locale",{months:["ינואר","פברואר","מרץ","אפריל","מאי","יוני","יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"].map(function(t,e){return{id:e+1,name:t}}),days:[{abbr:"א",name:"ראשון",id:1},{abbr:"ב",name:"שני",id:2},{abbr:"ג",name:"שלישי",id:3},{abbr:"ד",name:"רביעי",id:4},{abbr:"ה",name:"חמישי",id:5},{abbr:"ו",name:"שישי",id:6},{abbr:"ש",name:"שבת",id:7}],until:"עד ל"}),angular.module("RouteExplorer").factory("LocationBinder",["$location",function(t){return{bind:function(e,n,r,o,i){e[n]=t.search()[r]||null,e.$watch(n,function(e){i&&(e=i(e)),t.search(r,e)}),e.$watch(function(){return t.search()[r]||null},function(t){o&&(t=o(t)),e[n]=t})}}}]),angular.module("RouteExplorer").factory("TimeParser",[function(){function t(t){var e=Number(t.substr(0,4)),n=Number(t.substr(4,2));return new Date(e,n-1,1)}function e(e){var n=e.split("-",2),r=t(n[0]),o=n.length>1?t(n[1]):r,i=new Date(o.getFullYear(),o.getMonth()+1,1);return{from:r,to:o,end:i}}function n(t){return t.getFullYear()+("0"+(t.getMonth()+1)).slice(-2)}function r(t){var e=n(t.from);return t.from<t.to&&(e+="-"+n(t.to)),e}return{parseMonth:t,parsePeriod:e,formatMonth:n,formatPeriod:r}}]);
=======
(function() {
  var app = angular.module('RouteExplorer', ['ngRoute', 'ui.bootstrap', 'ui.bootstrap.buttons']);

  app.constant('env', {
    baseDir: '/static/ui/RouteExplorer'
  });

  app.config(['$routeProvider', 'env',
  function($routeProvider, env) {

      var templateUrl = function(templateName) {
          return env.baseDir + '/tpls/' + templateName + '.html';
      };

      $routeProvider
          .when('/', {
              pageId: 'welcome',
              templateUrl: templateUrl('SelectStops'),
              controller: 'SelectStopsController',
              resolve: { 'Layout': 'Layout' }
          })
          .when('/about', {
              pageId: 'about',
              templateUrl: templateUrl('About')
          })
          .when('/:period/select-route/:origin/:destination', {
              pageId: 'routes',
              templateUrl: templateUrl('SelectRoute'),
              controller: 'SelectRouteController',
              resolve: { 'Layout': 'Layout' },
              reloadOnSearch: false
          })
          .when('/:period/routes/:routeId', {
              pageId: 'route',
              templateUrl: templateUrl('RouteDetails'),
              controller: 'RouteDetailsController',
              resolve: { 'Layout': 'Layout' },
              reloadOnSearch: false
          })
          .otherwise({
              redirectTo: '/'
          });
  }]);
})();

// String.repeat polyfill
// taken from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/repeat#Polyfill
if (!String.prototype.repeat) {
  String.prototype.repeat = function(count) {
    'use strict';
    if (this === null) {
      throw new TypeError('can\'t convert ' + this + ' to object');
    }
    var str = '' + this;
    count = +count;
    if (count != count) {
      count = 0;
    }
    if (count < 0) {
      throw new RangeError('repeat count must be non-negative');
    }
    if (count == Infinity) {
      throw new RangeError('repeat count must be less than infinity');
    }
    count = Math.floor(count);
    if (str.length === 0 || count === 0) {
      return '';
    }
    // Ensuring count is a 31-bit integer allows us to heavily optimize the
    // main part. But anyway, most current (August 2014) browsers can't handle
    // strings 1 << 28 chars or longer, so:
    if (str.length * count >= 1 << 28) {
      throw new RangeError('repeat count must not overflow maximum string size');
    }
    var rpt = '';
    for (;;) {
      if ((count & 1) == 1) {
        rpt += str;
      }
      count >>>= 1;
      if (count === 0) {
        break;
      }
      str += str;
    }
    return rpt;
  };
}

angular.module('RouteExplorer').controller('AppController',
['$scope', '$location',
function($scope, $location) {
    $scope.share = function(prefix) {
        var url = prefix + encodeURIComponent('http://otrain.org/#' + $location.url());
        window.open(url, 'sharePopup', 'width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no');
    };

    $scope.$on('$routeChangeSuccess', function(e, route) {
        $scope.bodyClass = route.pageId ? 'rex-page-' + route.pageId : null;
    });
}]);

angular.module('RouteExplorer').controller('RouteDetailsController',
['$scope', '$route', '$http', '$location', 'LocationBinder', 'Layout', 'Locale', 'TimeParser',
function($scope, $route, $http, $location, LocationBinder, Layout, Locale, TimeParser) {
    var routeParams = $route.current.params;

    var period = TimeParser.parsePeriod(routeParams.period);
    var startDate = period.from;
    var endDate = period.end;

    var routeId = routeParams.routeId;
    var stopIds = Layout.findRoute(routeId).stops;
    var statsMap = {};

    $scope.loaded = false;
    $scope.stopIds = stopIds;
    $scope.origin = stopIds[0];
    $scope.destination = stopIds[stopIds.length - 1];

    $scope.selectedPeriod = formatMonth(period.from);
    if (period.to > period.from) {
        $scope.selectedPeriod += " \u2014 " + formatMonth(period.to)
    }

    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    $scope.selectRouteUrl = '#/' + routeParams.period + '/select-route/' + $scope.origin + '/' + $scope.destination;

    var previousPeriod = offsetPeriod(period, -1);
    var nextPeriod = offsetPeriod(period, +1);
    var bounds = Layout.getRoutesDateRange();

    $scope.previousPeriodUrl = bounds.min < previousPeriod.from ? '#/' + TimeParser.formatPeriod(previousPeriod) + '/routes/' + routeId : null;
    $scope.nextPeriodUrl = bounds.max > nextPeriod.to ? '#/' + TimeParser.formatPeriod(nextPeriod) + '/routes/' + routeId : null;

    $http.get('/api/route-info-full', { params: { route_id: routeId, from_date: startDate.getTime(), to_date: endDate.getTime() } })
        .success(function(data) {
            loadStats(data);
            $scope.loaded = true;
        });

    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

            return stop.name;
    };

    $scope.isDayEmpty = function(day) {
        var dayId = day.id;
        var dayTimes = statsMap[dayId];

        if (!dayTimes)
            return true;

        for (var time in dayTimes)
            if (dayTimes[time].info.num_trips > 0)
                return false;

        return true;
    };

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.tripCount = function(dayId, timeId) {
      var stats = getStats(dayId, timeId);
      if (!stats)
        return 0;

      return stats.info.num_trips;
    };

    function getStats(dayId, timeId) {
      dayId = dayId || 'all';
      timeId = timeId || 'all';
      return statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId] : null;
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    function loadStats(data) {
        $scope.times = [];
        var timesMap = {};

        for (var i in data) {
            var statGroup = data[i];
            var timeId = statGroup.info.hours == 'all' ? 'all' : statGroup.info.hours[0] + '-' + statGroup.info.hours[1];
            var dayId = statGroup.info.week_day;

            if (!statsMap[dayId])
                statsMap[dayId] = {};

            statsMap[dayId][timeId] = statGroup;

            if (timeId != 'all' && !timesMap[timeId]) {
                var time = {
                    id: timeId,
                    from: formatHour(statGroup.info.hours[0]),
                    to: formatHour(statGroup.info.hours[1])
                };
                timesMap[timeId] = time;
                $scope.times.push(time);
            }
        }
    }

    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function offsetMonth(date, offset) {
        var d = new Date(date);
        d.setMonth(d.getMonth() + offset);
        return d;
    }

    function offsetPeriod(period, offset) {
        size =
            (period.to.getFullYear() - period.from.getFullYear()) * 12 +
            period.to.getMonth() - period.from.getMonth() + 1;

        return {
            from: offsetMonth(period.from, size * offset),
            to: offsetMonth(period.to, size * offset),
            end: offsetMonth(period.end, size * offset)
        };
    }
}]);

angular.module('RouteExplorer').controller('SelectRouteController',
['$scope', '$http', '$location', '$route', 'Layout', 'TimeParser',
function($scope, $http, $location, $route, Layout, TimeParser) {
    $scope.stops = Layout.getStops();
    var period = TimeParser.parsePeriod($route.current.params.period);
    var origin = Layout.findStop($route.current.params.origin);
    var destination = Layout.findStop($route.current.params.destination);

    $http.get('/api/path-info-full', { params: {
        origin: origin.id,
        destination: destination.id,
        from_date: period.from.getTime(),
        to_date: period.end.getTime() }
    }).success(function(data) {
            loadStats(data);
            $scope.loaded = true;
    });

    var statsMap = {};

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }


    function loadStats(data) {
        $scope.stats = data;
    }

    Layout.findRoutesByPeriod(origin.id, destination.id, period.from, period.end).then(function(routes) {
        if (routes.length > 1)
            collapseRoutes(routes);
        $scope.routes = routes;

    });

    function stopName(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.name;
    }

    $scope.isCollapsed = function(value) {
        return angular.isArray(value);
    };

    $scope.isOrigin = function(stopId) {
        return stopId == origin.id;
    };

    $scope.isDestination = function(stopId) {
        return stopId == destination.id;
    };

    $scope.stopText = function(stopId) {
        if ($scope.isCollapsed(stopId))
            return "\u2022".repeat(stopId.length);

        return stopName(stopId);
    };

    $scope.stopTooltip = function(stopId) {
        if (!$scope.isCollapsed(stopId))
            return null;

        return stopId.map(stopName).join(", ");
    };

    $scope.barWidth = function(route) {
        var percentWidth = route.count * 100.0 / $scope.routes[0].count;

        if (percentWidth < 1.0)
            return "1px";

        return percentWidth + "%";
    };

    $scope.routeUrl = function(route) {
        return '/#/' + $route.current.params.period + '/routes/' + route.id;
    };

    function collapseRoutes(routes) {
        var collapsibleStops = findCommonStops(countStopFrequencies(routes), routes.length);
        delete collapsibleStops[origin.id];
        delete collapsibleStops[destination.id];

        for (var routeIndex in routes) {
            routes[routeIndex].stops = collapseStops(routes[routeIndex].stops, collapsibleStops);
        }

        function countStopFrequencies(routes) {
            var stopFrequencies = {};
            for (var routeIndex in routes) {
                var route = routes[routeIndex];
                for (var i in route.stops) {
                    var stopId = route.stops[i];
                    if (!stopFrequencies[stopId])
                        stopFrequencies[stopId] = 0;
                    stopFrequencies[stopId]++;
                }
            }

            return stopFrequencies;
        }

        function findCommonStops(stopFrequencies, routesCount) {
            var commonStops = {};
            for (var stopId in stopFrequencies)
                if (stopFrequencies[stopId] == routesCount)
                    commonStops[stopId] = true;

            return commonStops;
        }

        function collapseStops(stops, collapsibleStops) {
            var collapsed = [];
            var accumulator;

            for (var i in stops) {
                var stopId = stops[i];
                if (i > 0 && i < stops.length - 1 && collapsibleStops[stopId]) {
                    if (!accumulator) {
                        accumulator = [];
                        collapsed.push(accumulator);
                    }
                    accumulator.push(stopId);
                } else {
                    accumulator = null;
                    collapsed.push(stopId);
                }
            }

            return collapsed;
        }
    }
}]);

angular.module('RouteExplorer').controller('SelectStopsController',
['$scope', '$rootScope', '$location', 'Layout', 'Locale', 'TimeParser',
function($scope, $rootScope, $location, Layout, Locale, TimeParser) {
    $scope.stops = Layout.getStops();
    $scope.origin = null;
    $scope.destination = null;
    $scope.months = Locale.months;

    var dateRange = Layout.getRoutesDateRange();
    $scope.periods = generatePeriods(dateRange.min, dateRange.max);
    $scope.startPeriod = $scope.periods[0];
    $scope.endPeriod = $scope.periods[0];

    $scope.formValid = function() {
        return (
            !!$scope.origin &&
            !!$scope.destination &&
            $scope.origin != $scope.destination &&
            $scope.startPeriod.from <= $scope.endPeriod.to
        );
    };

    $scope.stopName = function(stopId) {
        var stop = Layout.findStop(stopId);
        if (!stop)
            return null;

        return stop.name;
    };

    $scope.goToRoutes = function() {
        $scope.noRoutes = false;
        $scope.loading = true;
        var period = {
            from: $scope.startPeriod.from,
            to: $scope.endPeriod.to,
            end: $scope.endPeriod.end,
        };
        var fromDate = period.from;
        var toDate = period.end;
        var periodStr = TimeParser.formatPeriod(period);
        Layout.findRoutesByPeriod($scope.origin.id, $scope.destination.id, fromDate, toDate)
            .then(function(routes) {
                if (routes.length === 0) {
                    $scope.noRoutes = true;
                } else if (routes.length == 1) {
                    $location.path('/' + periodStr + '/routes/' + routes[0].id);
                } else {
                    $location.path('/' + periodStr + '/select-route/' + $scope.origin.id + '/' + $scope.destination.id);
                }
            })
            .finally(function() {
                $scope.loading = false;
            });
    };

    $scope.dismissError = function() {
        $scope.noRoutes = false;
    };

    function generatePeriods(fromDate, toDate) {
      // fromDate=1970-1-1 due to a data bug. This is a quick temporary workaround
      if (fromDate.getFullYear() < 2013) fromDate = new Date(2013, 0, 1);

      var periods = [];
      var start = new Date(fromDate.getFullYear(), fromDate.getMonth(), 1);
      while (start < toDate) {
        end = new Date(start.getFullYear(), start.getMonth() + 1, start.getDate());
        var period = {
          from: start,
          to: start,
          end: end,
          name: Locale.months[start.getMonth()].name + " " + start.getFullYear()
        };
        period.toName = Locale.until + period.name;
        periods.push(period);
        start = end;
      }
      periods.reverse();
      return periods;
    }
}]);

angular.module('RouteExplorer').controller('TimesDetailsController',
    ['$scope', '$route', 'Locale','LocationBinder','Layout',
function($scope, $route, Locale, LocationBinder, Layout) {
    Layout.then(function(Layout) {
        $scope.layout = Layout;
    });
    $scope.layout = null;

    var statsMap = {};
    var routeParams = $route.current.params;
    $scope.stopIds = [parseInt(routeParams.origin), parseInt(routeParams.destination)];
    LocationBinder.bind($scope, 'selectedDay', 'day', function(val) { return val ? Number(val) : null; });
    LocationBinder.bind($scope, 'selectedTime', 'time');
    function formatHour(hour) {
        return ('0' + hour % 24 + '').slice(-2) + ':00';
    }

    function formatMonth(date) {
        return Locale.months[date.getMonth()].name + ' ' + date.getFullYear()
    }

    function selectedStats() {
        var stats = getStats($scope.selectedDay, $scope.selectedTime);
        if (stats)
          return stats.stops;

        return [];
    }

    $scope.stopName = function(stopId) {
        if ($scope.layout) {
            var stop = $scope.layout.findStop(stopId);
            if (!stop)
                return null;

            return stop.name;
        } else {
            return null;
        }
    };

    $scope.selectedDay = null;
    $scope.days = Locale.days;

    $scope.selectedTime = null;
    $scope.times = [];

    $scope.loadStats = function() {
        var data = $scope.stats;
        $scope.times = [];
        var timesMap = {};

        for (var i in data) {
            var statGroup = data[i];
            var timeId = statGroup.info.hours == 'all' ? 'all' : statGroup.info.hours[0] + '-' + statGroup.info.hours[1];
            var dayId = statGroup.info.week_day;

            if (!statsMap[dayId])
                statsMap[dayId] = {};

            statsMap[dayId][timeId] = statGroup;

            if (timeId != 'all' && !timesMap[timeId]) {
                var time = {
                    id: timeId,
                    from: formatHour(statGroup.info.hours[0]),
                    to: formatHour(statGroup.info.hours[1])
                };
                timesMap[timeId] = time;
                $scope.times.push(time);
            }
        }
    };
    $scope.tripCount = function(dayId, timeId) {
      var stats = getStats(dayId, timeId);
      if (!stats)
        return 0;

      return stats.info.num_trips;
    };

    function getStats(dayId, timeId) {
      dayId = dayId || 'all';
      timeId = timeId || 'all';
      return statsMap[dayId] && statsMap[dayId][timeId] ? statsMap[dayId][timeId] : null;
    }

    $scope.isTimeEmpty = function(time) {
        var dayId = $scope.selectedDay || 'all';
        var timeId = time.id;

        var timeStats = statsMap[dayId] && statsMap[dayId][timeId];
        if (timeStats && timeStats.info.num_trips > 0)
            return false;

        return true;
    };

    $scope.stopStats = function(stopId) {
        var stats = selectedStats();
        for (var i in stats) {
            if (stats[i].stop_id == stopId)
                return stats[i];
        }
        return null;
    };

    $scope.loadStats();
}]);


angular.module('RouteExplorer').directive("rexPercentBar",
['env',
function(env) {
    return {
        restrict: 'E',
        scope: {
          value: '=value',
          type: '=type'
        },
        templateUrl: env.baseDir + '/tpls/PercentBar.html'
      };
}]);

angular.module('RouteExplorer').directive("timesDetails",
['env','Layout',
function(env, Layout) {
    return {
        restrict: 'E',
        scope: {
            stats: '='
        },
        controller: 'TimesDetailsController',
        templateUrl: env.baseDir + '/tpls/TimesDetails.html'
      };
}]);

angular.module('RouteExplorer').filter('duration', function() {
    return function(seconds) {
        var negative = false;
        seconds = Math.trunc(seconds);
        if (seconds < 0) {
            negative = true;
            seconds = -seconds;
        }

        var minutes = Math.trunc(seconds / 60);
        seconds -= minutes * 60;
        var hours = Math.trunc(minutes / 60);
        minutes -= hours * 60;

        if (seconds < 10) seconds = '0' + seconds;
        if (minutes < 10 && hours !== 0) minutes = '0' + minutes;

        var res = minutes + ':' + seconds;
        if (hours !== 0)
            res = hours + ':' + res;

        if (negative)
            res = '-' + res;

        return res;
    };
});

angular.module('RouteExplorer').factory('Layout',
['$http', '$q',
function($http, $q) {
    var self = this;
    var stops = [];
    var stopsMap = {};
    var routes = [];
    var routesMap = {};

    var loadedPromise = $q.all([
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

    var getRoutesDateRange = function() {
        var max = new Date(1900, 0, 1);
        var min = new Date(2100, 0, 1);

        for (var i in routes) {
            route = routes[i];
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

    service = {
        getStops: function() { return stops; },
        getRoutes: function() { return routes; },
        findRoute: findRoute,
        findStop: findStop,
        findRoutes: function(origin, destination) { return findRoutes(routes, origin, destination); },
        findRoutesByPeriod: findRoutesByPeriod,
        getRoutesDateRange: getRoutesDateRange
    };

    return loadedPromise.then(function() { return service; });
}]);

angular.module('RouteExplorer').constant('Locale', {
  months: [
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
  ].map(function(v, i) { return { id: i + 1, name: v }; }),

  days: [
      { abbr: 'א', name: 'ראשון', id: 1 },
      { abbr: 'ב', name: 'שני', id: 2 },
      { abbr: 'ג', name: 'שלישי', id: 3 },
      { abbr: 'ד', name: 'רביעי', id: 4 },
      { abbr: 'ה', name: 'חמישי', id: 5 },
      { abbr: 'ו', name: 'שישי', id: 6 },
      { abbr: 'ש', name: 'שבת', id: 7 }
  ],
  until: 'עד ל'
});

angular.module('RouteExplorer').factory('LocationBinder',
['$location',
function($location) {
    return {
        bind: function(scope, scopeProperty, locationProperty, parser, formatter) {
            scope[scopeProperty] = $location.search()[locationProperty] || null;

            scope.$watch(scopeProperty, function(value) {
                if (formatter)
                    value = formatter(value);

                $location.search(locationProperty, value);
            });

            scope.$watch(function() { return $location.search()[locationProperty] || null; }, function(value) {
                if (parser)
                    value = parser(value);

                scope[scopeProperty] = value;
            });
        }
    };
}]);

angular.module('RouteExplorer').factory('TimeParser',
[
function() {
    function parseMonth(monthString) {
        var year = Number(monthString.substr(0, 4));
        var month = Number(monthString.substr(5, 2));
        return new Date(year, month - 1, 1);
    }

    function parsePeriod(periodString) {
        var parts = periodString.split('-', 2);
        var from = parseMonth(parts[0]);
        var to = parts.length > 1 ? parseMonth(parts[1]) : from;
        var end = new Date(to.getFullYear(), to.getMonth() + 1, 1);
        return { from: from, to: to, end: end };
    }

    function formatMonth(date) {
        return date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2);
    }

    function formatPeriod(period) {
        var f = formatMonth(period.from);
        if (period.from < period.to)
            f += '-' + formatMonth(period.to);

        return f;
    }

    return {
        parseMonth: parseMonth,
        parsePeriod: parsePeriod,
        formatMonth: formatMonth,
        formatPeriod: formatPeriod
    }
}]);

>>>>>>> eran-ui-range
//# sourceMappingURL=app.js.map
