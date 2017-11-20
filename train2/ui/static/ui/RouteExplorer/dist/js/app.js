"use strict";!function(){var t=angular.module("RouteExplorer",["ngRoute","ui.bootstrap","ui.bootstrap.buttons","leaflet-directive","highcharts-ng"]);t.constant("env",{baseDir:"/static/ui/RouteExplorer"}),t.config(["$routeProvider","env",function(t,e){var r=function(t){return e.baseDir+"/tpls/"+t+".html"};t.when("/",{pageId:"welcome",templateUrl:r("SelectStops"),controller:"SelectStopsController",resolve:{Layout:"Layout"}}).when("/about",{pageId:"about",templateUrl:r("About")}).when("/:period/select-route/:origin/:destination",{pageId:"routes",templateUrl:r("SelectRoute"),controller:"SelectRouteController",resolve:{Layout:"Layout"},reloadOnSearch:!1}).when("/:period/routes/:routeId",{pageId:"route",templateUrl:r("RouteDetails"),controller:"RouteDetailsController",resolve:{Layout:"Layout"},reloadOnSearch:!1}).when("/heat-map",{pageId:"heatMap",templateUrl:r("HeatMap"),controller:"HeatMapController",reloadOnSearch:!1,resolve:{Layout:"Layout"}}).when("/graphs",{pageId:"graphs",templateUrl:r("Graphs"),controller:"GraphsController",reloadOnSearch:!1,resolve:{Layout:"Layout"}}).when("/routes",{pageId:"routes",templateUrl:r("RealRoutes"),controller:"RealRoutesController",reloadOnSearch:!1,resolve:{Layout:"Layout"}}).when("/highlights",{pageId:"highlights",templateUrl:r("Highlights"),controller:"HighlightsController",reloadOnSearch:!1,resolve:{Layout:"Layout"}}).when("/top-highlights",{pageId:"top_highlights",templateUrl:r("TopHighlights"),controller:"TopHighlightsController",reloadOnSearch:!1,resolve:{Layout:"Layout"}}).otherwise({redirectTo:"/"})}])}(),String.prototype.repeat||(String.prototype.repeat=function(t){if(null===this)throw new TypeError("can't convert "+this+" to object");var e=""+this;if(t=+t,t!=t&&(t=0),t<0)throw new RangeError("repeat count must be non-negative");if(t==1/0)throw new RangeError("repeat count must be less than infinity");if(t=Math.floor(t),0===e.length||0===t)return"";if(e.length*t>=1<<28)throw new RangeError("repeat count must not overflow maximum string size");for(var r="";1==(1&t)&&(r+=e),t>>>=1,0!==t;)e+=e;return r}),angular.module("RouteExplorer").directive("rexPercentBar",["env",function(t){return{restrict:"E",scope:{value:"=value",type:"=type"},templateUrl:t.baseDir+"/tpls/PercentBar.html"}}]),angular.module("RouteExplorer").directive("timesDetails",["env","Layout",function(t,e){return{restrict:"E",scope:{stats:"="},controller:"TimesDetailsController",templateUrl:t.baseDir+"/tpls/TimesDetails.html"}}]);var daysTable={0:"ראשון",1:"שני",2:"שלישי",3:"רביעי",4:"חמישי",5:"שישי",6:"שבת"};angular.module("RouteExplorer").filter("week_day1",function(){return function(t){return"all"==t?"כל הימים":daysTable[t-1]||"??? "+t}}).filter("week_day0",function(){return function(t){return"all"==t?"כל הימים":daysTable[t]||"??? "+t}}).filter("hours",function(){return function(t){var e=function(t){return t>=24?t%24:t};if("all"==t)return"כל היום";var r=e(t[1]),n=e(t[0]);return r+" - "+n}}).filter("month_name",function(){var t=["ינואר","פברואר","מרץ","אפריל","מאי","יוני","יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"];return function(e){return t[e-1]}}),angular.module("RouteExplorer").filter("duration",function(){return function(t){var e=!1;t=Math.trunc(t),t<0&&(e=!0,t=-t);var r=Math.trunc(t/60);t-=60*r;var n=Math.trunc(r/60);r-=60*n,t<10&&(t="0"+t),r<10&&0!==n&&(r="0"+r);var o=r+":"+t;return 0!==n&&(o=n+":"+o),e&&(o="-"+o),o}}),angular.module("RouteExplorer").controller("AppController",["$scope","$location",function(t,e){"ngInject";t.share=function(t){var r=t+encodeURIComponent("http://otrain.org/#"+e.url());window.open(r,"sharePopup","width=600,height=550,top=100,left=100,location=no,scrollbar=no,status=no,menubar=no")},t.$on("$routeChangeSuccess",function(e,r){t.bodyClass=r.pageId?"rex-page-"+r.pageId:null})}]),angular.module("RouteExplorer").constant("daysTable",[{value:0,name:"ראשון"},{value:1,name:"שני"},{value:2,name:"שלישי"},{value:3,name:"רביעי"},{value:4,name:"חמישי"},{value:5,name:"שישי"},{value:6,name:"שבת"}]).constant("monthNames",["dummy","ינואר","פברואר","מרץ","אפריל","מאי","יוני","יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"]).constant("hoursList",[{name:"4-7",values:[4,5,6]},{name:"7-9",values:[7,8]},{name:"9-12",values:[9,10,11]},{name:"12-15",values:[12,13,14]},{name:"15-18",values:[15,16,17]},{name:"18-21",values:[18,19,20]},{name:"21-24",values:[21,22,23]},{name:"24-4",values:[0,1,2,3]}]),angular.module("RouteExplorer").controller("GraphsController",["$scope","$http","$q","$timeout","$location","Layout","daysTable","hoursList","monthNames",function(t,e,r,n,o,a,i,u,l){"ngInject";t.wip=!0,t.Layout=a,t.input={graphKind:"perDay"},t.updateSkipped=function(){t.refresh({skippedCall:!0})},t.actualFromToStops=function(){return t.fromToStops.filter(function(t){return!t.skipOnly})},t.getSkipped=function(){if(t.fromToStops)return t.fromToStops.filter(function(t){return t.skipOnly}).map(function(t){return t.id}).join(",")},t.refresh=function(n){n=n||{},t.wip=!0,t.startStop=t.input.startStop,t.endStop=t.input.endStop,t.startDate=t.input.startDate.value,t.endDate=t.input.endDate.value,o.search({startStop:t.startStop.id,endStop:t.endStop.id,startDate:t.startDate,endDate:t.endDate}),t.stops=a.getStops(),t.stopsById={},t.stops.forEach(function(e){t.stopsById[e.id]=e});var i=[e.get("/api/v1/stats/from-to-full/",{params:{from_date:t.startDate,to_date:t.endDate,from_stop:t.startStop.id,to_stop:t.endStop.id,skipped:n.skippedCall?t.getSkipped():void 0}}).then(function(e){t.stat=e.data.table})];n.skippedCall||i.push(e.get("/api/v1/stops/from-to/",{params:{from_stop:t.startStop.id,to_stop:t.endStop.id}}).then(function(e){t.fromToStopsIds=e.data,t.fromToStops=t.fromToStopsIds.map(function(e){return t.stopsById[e]});var r=!0,n=!1,o=void 0;try{for(var a,i=t.fromToStops[Symbol.iterator]();!(r=(a=i.next()).done);r=!0){var u=a.value;u.skipOnly=!1}}catch(l){n=!0,o=l}finally{try{!r&&i["return"]&&i["return"]()}finally{if(n)throw o}}})),r.all(i).then(function(){t.wip=!1,t.updateChart()})},t.getRouteTitle=function(t){return"מ"+t.from+" ל"+t.to+" ("+t.count+" נסיעות)"},t.initData=function(){return t.buildDates()},t.buildDates=function(){return e.get("/api/v1/general/dates-range").then(function(e){var r=e.data,n=[r.first_date.month,r.first_date.year],o=[r.last_date.month,r.last_date.year];t.buildDatesRange(n,o)})},t.buildDatesRange=function(e,r){for(t.startDates=[],t.endDates=[];;){t.startDates.push({name:l[e[0]]+" "+e[1],value:"1-"+e[0]+"-"+e[1]});var n=12==e[0]?[1,e[1]+1]:[e[0]+1,e[1]];if(t.endDates.push({name:l[e[0]]+" "+e[1],value:"1-"+n[0]+"-"+n[1]}),t.startDates.length>100)return void alert("error");if(e[0]==r[0]&&e[1]==r[1])return;e=[n[0],n[1]]}},t.computePerDaySeries=function(){var e={};t.stat.forEach(function(t){var r=t.stop_id+"-"+t.week_day_local;e[r]=e[r]||{num_trips:0,arrival_late_count:0},e[r].num_trips+=t.num_trips,e[r].arrival_late_count+=t.arrival_late_count});var r=[];return i.forEach(function(n){var o=t.actualFromToStops().map(function(t){var r=e[t.id+"-"+n.value],o={};return r?(o.y=100*r.arrival_late_count/r.num_trips,o.numTrips=r.num_trips):(o.y=0,o.numTrips=0,console.log("no entry for "+t.id+" "+n.value)),o.lineName=n.name,o});r.push({name:n.name,data:o})}),r},t.computePerHoursSeries=function(){var e={},r={};u.forEach(function(t){t.values.forEach(function(e){r[e]=t})}),t.stat.forEach(function(t){var n=r[t.hour_local].name,o=t.stop_id+"-"+n;e[o]=e[o]||{num_trips:0,arrival_late_count:0},e[o].num_trips+=t.num_trips,e[o].arrival_late_count+=t.arrival_late_count});var n=[];return u.forEach(function(r){var o=t.actualFromToStops().map(function(t){var n=e[t.id+"-"+r.name],o={};return n?(o.y=100*n.arrival_late_count/n.num_trips,o.numTrips=n.num_trips):(console.log("no entry for "+t.id+" "+r.name),o.y=0,o.numTrips=0),o.lineName=r.name,o});n.push({name:r.name,data:o})}),n},t.updateChart=function(){var e=t.actualFromToStops().map(function(t,e){return t.name+" - "+(e+1)});t.perDaySeries=t.computePerDaySeries(),t.perHoursSeries=t.computePerHoursSeries();var r={formatter:function(){var t=Math.round(100*this.y)/100;return'<span dir="rtl"><b>'+this.x+"</b><br/><span>"+this.point.lineName+"</span><br/><span>רכבות מאחרות:</span>"+t+"%<br/><span>מספר רכבות: </span>"+this.point.numTrips+"</span>"},useHTML:!0};t.chartPerDay={options:{chart:{type:"line"},title:{text:"איחור בחתך יומי"},tooltip:r},xAxis:{reversed:!0,categories:e,useHTML:!0},yAxis:{opposite:!0,useHTML:!0,title:{text:"אחוזי איחור"}},series:t.perDaySeries},t.chartPerHour={options:{chart:{type:"line"},title:{text:"אישור בחתך שעתי"},tooltip:r},yAxis:{useHTML:!0,opposite:!0,title:{text:"אחוזי איחור"}},xAxis:{useHTML:!0,reversed:!0,categories:e},tooltip:{useHTML:!0},series:t.perHoursSeries}},t.findDate=function(t,e){for(var r=0;r<t.length;r++)if(t[r].value==e)return t[r];return null},t.initData().then(function(){var e=o.search();t.input.startDate=t.findDate(t.startDates,e.startDate)||t.startDates[t.startDates.length-1],t.input.endDate=t.findDate(t.endDates,e.endDate)||t.endDates[t.endDates.length-1],t.input.startStop=a.findStop(e.startStop||400),t.input.endStop=a.findStop(e.endStop||3700),t.refresh()})}]),angular.module("RouteExplorer").controller("HeatMapController",["$scope","$http","Layout",function(t,e,r){"ngInject";t.Layout=r;var n=t.Layout.findStop(4600);console.log(n),angular.extend(t,{defaults:{scrollWheelZoom:!1},center:{lat:n.latlon[0],lng:n.latlon[1],zoom:10}}),t.stops=r.getStops(),t.input={stop:t.stops[0]},t.paths=[],e.get("/api/v1/heat-map/").then(function(e){t.heatmapData=e.data,t.heatmapData.forEach(function(e){var r=t.Layout.findStop(e.stop_id).latlon,n=255-Math.floor(255*e.score),o="rgb(255,"+n+",0)",a=t.Layout.findStop(e.stop_id).name+"<br/>"+Math.floor(100*e.score)/100;t.paths.push({color:o,fillColor:o,fillOpacity:1,type:"circleMarker",stroke:!1,radius:10,latlngs:r,message:a,popupOptions:{className:"ot-popup"}})})})}]),angular.module("RouteExplorer").controller("HighlightsController",["$scope","$http","$q","$timeout","$location","Layout","daysTable","hoursList","monthNames",function(t,e,r,n,o,a,i,u,l){"ngInject";t.init=function(){e.get("/api/v1/highlights/").then(function(e){t.highlights=e.data.highlights,t.url=e.data.url,t.fields=[{name:"תאריך",sortKey:function(t){return 100*t.year+t.month}},{name:"מספר נסיעות",sortKey:function(t){return t.num_trips},initialDesc:!0},{name:"יום בשבוע",sortKey:function(t){return"all"==t.week_day?-1:t.week_day}},{name:"שעות",sortKey:function(t){return"all"==t.hours?-1:t.hours[1]}},{name:"% איחורים מעל 5 דקות",active:!0,asc:!1,initialDesc:!0,sortKey:function(t){return t.mean_arrival_late_pct}},{name:"קישור",disableSort:!0}],t.refresh()})},t.sortBy=function(e){var r=!0,n=!1,o=void 0;try{for(var a,i=t.fields[Symbol.iterator]();!(r=(a=i.next()).done);r=!0){var u=a.value;u!=e&&(u.active=!1)}}catch(l){n=!0,o=l}finally{try{!r&&i["return"]&&i["return"]()}finally{if(n)throw o}}e.active?e.asc=!e.asc:(e.active=!0,e.asc=!e.initialDesc),t.refresh()},t.refresh=function(){var e=null,r=!0,n=!1,o=void 0;try{for(var a,i=t.fields[Symbol.iterator]();!(r=(a=i.next()).done);r=!0){var u=a.value;u.active&&(e=u)}}catch(l){n=!0,o=l}finally{try{!r&&i["return"]&&i["return"]()}finally{if(n)throw o}}e&&t.highlights.sort(function(t,r){var n=e.sortKey(t),o=e.sortKey(r),a=e.asc?1:-1;return n>o?1*a:n<o?-1*a:0})},t.init()}]),angular.module("RouteExplorer").controller("RouteDetailsController",["$scope","$route","$http","$location","LocationBinder","Layout","Locale","TimeParser",function(t,e,r,n,o,a,i,u){"ngInject";function l(t,e){return t=t||"all",e=e||"all",_[t]&&_[t][e]?_[t][e]:null}function s(){var e=l(t.selectedDay,t.selectedTime);return e?e.stops:[]}function c(e){t.times=[];var r={};for(var n in e){var o=e[n],a="all"==o.info.hours?"all":o.info.hours[0]+"-"+o.info.hours[1],i=o.info.week_day;if(_[i]||(_[i]={}),_[i][a]=o,"all"!=a&&!r[a]){var u={id:a,from:p(o.info.hours[0]),to:p(o.info.hours[1])};r[a]=u,t.times.push(u)}}}function p(t){return("0"+t%24).slice(-2)+":00"}function d(t){return i.months[t.getMonth()].name+" "+t.getFullYear()}function f(t,e){var r=new Date(t);return r.setMonth(r.getMonth()+e),r}function m(t,e){var r=12*(t.to.getFullYear()-t.from.getFullYear())+t.to.getMonth()-t.from.getMonth()+1;return{from:f(t.from,r*e),to:f(t.to,r*e),end:f(t.end,r*e)}}var h=e.current.params,g=u.parsePeriod(h.period),v=u.createRequestString(g.from),y=u.createRequestString(g.end),S=h.routeId,D=a.findRoute(S).stops,_={};t.loaded=!1,t.stopIds=D,t.origin=D[0],t.destination=D[D.length-1],t.selectedPeriod=d(g.from),g.to>g.from&&(t.selectedPeriod+=" — "+d(g.to)),t.selectedDay=null,t.days=i.days,t.selectedTime=null,t.times=[],t.selectRouteUrl="#/"+h.period+"/select-route/"+t.origin+"/"+t.destination;var b=m(g,-1),R=m(g,1),T=a.getRoutesDateRange(),x=864e6;t.previousPeriodUrl=T.min.getTime()-x<b.from.getTime()?"#/"+u.formatPeriod(b)+"/routes/"+S:null,t.nextPeriodUrl=T.max>R.to?"#/"+u.formatPeriod(R)+"/routes/"+S:null,r.get("/api/v1/stats/route-info-full",{params:{route_id:S,from_date:v,to_date:y}}).success(function(e){c(e),t.loaded=!0}),o.bind(t,"selectedDay","day",function(t){return t?Number(t):null}),o.bind(t,"selectedTime","time"),t.stopStats=function(t){var e=s();for(var r in e)if(e[r].stop_id==t)return e[r];return null},t.stopName=function(t){var e=a.findStop(t);return e?e.name:null},t.isDayEmpty=function(t){var e=t.id,r=_[e];if(!r)return!0;for(var n in r)if(r[n].info.num_trips>0)return!1;return!0},t.isTimeEmpty=function(e){var r=t.selectedDay||"all",n=e.id,o=_[r]&&_[r][n];return!(o&&o.info.num_trips>0)},t.tripCount=function(t,e){var r=l(t,e);return r?r.info.num_trips:0}}]),angular.module("RouteExplorer").controller("RealRoutesController",["$scope","$http","$q","$timeout","$location","Layout","daysTable","hoursList","monthNames",function(t,e,r,n,o,a,i,u,l){"ngInject";t.selectedYear=2017,t.selectedMonth=9,t.getMonths=function(){return[1,2,3,4,5,6,7,8,9,10,11,12]},t.getYears=function(){for(var t=[],e=(new Date).getFullYear(),r=2015;r<=e;)t.push(r),r++;return t},t.init=function(){t.months=t.getMonths(),t.years=t.getYears()},t.refresh=function(){t.realRoutes=null;var r=t.selectedYear,n=t.selectedMonth;e.get("/api/v1/real-routes/"+r+"/"+n+"/").then(function(e){t.realRoutes=e.data;var r=!0,n=!1,o=void 0;try{for(var a,i=t.realRoutes[Symbol.iterator]();!(r=(a=i.next()).done);r=!0){var u=a.value;console.log(u),u.firstStop=u.stops[0],u.lastStop=u.stops[u.stops.length-1]}}catch(l){n=!0,o=l}finally{try{!r&&i["return"]&&i["return"]()}finally{if(n)throw o}}})},t.init()}]),angular.module("RouteExplorer").controller("SelectRouteController",["$scope","$http","$location","$route","Layout","TimeParser",function(t,e,r,n,o,a){"ngInject";function i(e){t.stats=e}function u(t){var e=o.findStop(t);return e?e.name:null}t.stops=o.getStops();var l=a.parsePeriod(n.current.params.period),s=o.findStop(n.current.params.origin),c=o.findStop(n.current.params.destination),p=["startStop="+s.id,"endStop="+c.id,"startDate="+a.createRequestString(l.from,"-"),"endDate="+a.createRequestString(l.end,"-")];t.graphsUrl="#/graphs?"+p.join("&"),e.get("/api/v1/stats/path-info-full/",{params:{origin:s.id,destination:c.id,from_date:a.createRequestString(l.from),to_date:a.createRequestString(l.end)}}).success(function(e){i(e),t.loaded=!0});o.findRoutesByPeriod(s.id,c.id,l.from,l.end).then(function(e){t.routes=e}),t.isOrigin=function(t){return t==s.id},t.isDestination=function(t){return t==c.id},t.stopText=function(t){return u(t)},t.barWidth=function(e){var r=100*e.count/t.routes[0].count;return r<1?"1px":r+"%"},t.routeUrl=function(t){return"/#/"+n.current.params.period+"/routes/"+t.id}}]),angular.module("RouteExplorer").controller("SelectStopsController",["$scope","$rootScope","$location","Layout","Locale","TimeParser",function(t,e,r,n,o,a){"ngInject";function i(t,e){t.getFullYear()<2013&&(t=new Date(2013,0,1));for(var r=[],n=new Date(t.getFullYear(),t.getMonth(),1);n<e;){var a=new Date(n.getFullYear(),n.getMonth()+1,n.getDate()),i={from:n,to:n,end:a,name:o.months[n.getMonth()].name+" "+n.getFullYear()};i.toName=o.until+i.name,r.push(i),n=a}return r.reverse(),r}t.stops=n.getStops(),t.origin=null,t.destination=null,t.months=o.months;var u=n.getRoutesDateRange();t.periods=i(u.min,u.max),t.startPeriod=t.periods[0],t.endPeriod=t.periods[0],t.formValid=function(){return!!t.origin&&!!t.destination&&t.origin!=t.destination&&t.startPeriod.from<=t.endPeriod.to},t.stopName=function(t){var e=n.findStop(t);return e?e.name:null},t.goToRoutes=function(){t.noRoutes=!1,t.loading=!0;var e={from:t.startPeriod.from,to:t.endPeriod.to,end:t.endPeriod.end},o=e.from,i=e.end,u=a.formatPeriod(e);n.findRoutesByPeriod(t.origin.id,t.destination.id,o,i).then(function(e){0===e.length?t.noRoutes=!0:1==e.length?r.path("/"+u+"/routes/"+e[0].id):r.path("/"+u+"/select-route/"+t.origin.id+"/"+t.destination.id)})["finally"](function(){t.loading=!1})},t.dismissError=function(){t.noRoutes=!1}}]),angular.module("RouteExplorer").controller("TimesDetailsController",["$scope","$route","Locale","LocationBinder","Layout",function(t,e,r,n,o){"ngInject";function a(t){return("0"+t%24).slice(-2)+":00"}function i(){var e=u(t.selectedDay,t.selectedTime);return e?e.stops:[]}function u(t,e){return t=t||"all",e=e||"all",l[t]&&l[t][e]?l[t][e]:null}o.then(function(e){t.layout=e}),t.layout=null;var l={},s=e.current.params;t.stopIds=[parseInt(s.origin),parseInt(s.destination)],n.bind(t,"selectedDay","day",function(t){return t?Number(t):null}),n.bind(t,"selectedTime","time"),t.stopName=function(e){if(t.layout){var r=t.layout.findStop(e);return r?r.name:null}return null},t.selectedDay=null,t.days=r.days,t.selectedTime=null,t.times=[],t.loadStats=function(){var e=t.stats;t.times=[];var r={};for(var n in e){var o=e[n],i="all"==o.info.hours?"all":o.info.hours[0]+"-"+o.info.hours[1],u=o.info.week_day;if(l[u]||(l[u]={}),l[u][i]=o,"all"!=i&&!r[i]){var s={id:i,from:a(o.info.hours[0]),to:a(o.info.hours[1])};r[i]=s,t.times.push(s)}}},t.tripCount=function(t,e){var r=u(t,e);return r?r.info.num_trips:0},t.isTimeEmpty=function(e){var r=t.selectedDay||"all",n=e.id,o=l[r]&&l[r][n];return!(o&&o.info.num_trips>0)},t.stopStats=function(t){var e=i();for(var r in e)if(e[r].stop_id==t)return e[r];return null},t.loadStats()}]),angular.module("RouteExplorer").controller("TopHighlightsController",["$scope","$http","$q","$timeout","$location","Layout","daysTable","hoursList","monthNames",function(t,e,r,n,o,a,i,u,l){"ngInject";t.init=function(){e.get("/api/v1/highlights/top/").then(function(e){var r=e.data.highlights;t.highlightLists=[{kind:"late",title:"נסיעה באיחור",items:r.late,color:"danger"},{kind:"ontime",title:"נסיעה בזמן",items:r.ontime,color:"success"}]})},t.init()}]),angular.module("RouteExplorer").factory("Layout",["$http","$q","TimeParser",function(t,e,r){var n=[],o={},a=[],i={},u=e.all([t.get("/api/v1/stops/").then(function(t){n=t.data.map(function(t){return{id:t.stop_id,name:t.heb_stop_names[0],names:t.heb_stop_names,latlon:t.latlon}}),n.forEach(function(t){o[t.id]=t})}),t.get("/api/v1/routes/all/").then(function(t){a=t.data.map(function(t){return{id:t.id,stops:t.stop_ids,count:t.count,minDate:new Date(t.min_date),maxDate:new Date(t.max_date)}}),i=a.reduce(function(t,e){return t[e.id]=e,t},{})})]),l=function(t){return o[t]||null},s=function(t){return l(t).name},c=function(t,e,r){var n={};return t.forEach(function(t){var o=t.stops.indexOf(e),a=t.stops.indexOf(r);if(!(o<0||a<0||o>a)){var i=t.stops,u=t.id;u in n?n[u].count+=t.count:n[u]={id:u,stops:i,count:t.count}}}),n=Object.keys(n).map(function(t){return n[t]}),n.sort(function(t,e){return e.count-t.count}),n},p=function(n,o,i,u){var l=e.defer(),s=c(a,n,o);if(0===s.length)l.resolve([]);else{var p=i,d=u;t.get("/api/v1/routes/all-by-date/",{params:{from_date:r.createRequestString(p),to_date:r.createRequestString(d)}}).then(function(t){var e=t.data.map(function(t){return{id:t.id,stops:t.stop_ids,count:t.count}});l.resolve(c(e,n,o))},function(t){l.reject({msg:"Error fetching routes",response:t})})}return l.promise},d=function(t){return i[t]||null},f=function(){var t=new Date(1900,0,1),e=new Date(2100,0,1);for(var r in a){var n=a[r];0!==n.count&&(n.minDate&&n.minDate<e&&(e=n.minDate),n.maxDate&&n.maxDate>t&&(t=n.maxDate))}return{min:e,max:t}},m={getStops:function(){return n},getRoutes:function(){return a},findRoute:d,findStop:l,findStopName:s,findRoutes:function(t,e){return c(a,t,e)},findRoutesByPeriod:p,getRoutesDateRange:f};return u.then(function(){return m})}]),angular.module("RouteExplorer").constant("Locale",{months:["ינואר","פברואר","מרץ","אפריל","מאי","יוני","יולי","אוגוסט","ספטמבר","אוקטובר","נובמבר","דצמבר"].map(function(t,e){return{id:e+1,name:t}}),days:[{abbr:"א",name:"ראשון",id:1},{abbr:"ב",name:"שני",id:2},{abbr:"ג",name:"שלישי",id:3},{abbr:"ד",name:"רביעי",id:4},{abbr:"ה",name:"חמישי",id:5},{abbr:"ו",name:"שישי",id:6},{abbr:"ש",name:"שבת",id:7}],until:"עד ל"}),angular.module("RouteExplorer").factory("LocationBinder",["$location",function(t){return{bind:function(e,r,n,o,a){e[r]=t.search()[n]||null,e.$watch(r,function(e){a&&(e=a(e)),t.search(n,e)}),e.$watch(function(){return t.search()[n]||null},function(t){o&&(t=o(t)),e[r]=t})}}}]),angular.module("RouteExplorer").factory("TimeParser",[function(){function t(t,e){e=e||"/";var r=t.getDate().toString(),n=(t.getMonth()+1).toString(),o=t.getFullYear().toString();return r+e+n+e+o}function e(t){var e=Number(t.substr(0,4)),r=Number(t.substr(4,2));return new Date(e,r-1,1)}function r(t){var r=t.split("-",2),n=e(r[0]),o=r.length>1?e(r[1]):n,a=new Date(o.getFullYear(),o.getMonth()+1,1);return{from:n,to:o,end:a}}function n(t){return t.getFullYear()+("0"+(t.getMonth()+1)).slice(-2)}function o(t){var e=n(t.from);return t.from<t.to&&(e+="-"+n(t.to)),e}return{createRequestString:t,parseMonth:e,parsePeriod:r,formatMonth:n,formatPeriod:o}}]);
//# sourceMappingURL=app.js.map
