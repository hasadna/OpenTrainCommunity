"use strict";
var directives = angular.module('my.directives',['my.filters']);

directives.directive('trip',function() {
	return {
	    controller : 'TripController',
		scope : {
			tid : "=",
		},
		restrict : 'E',
		templateUrl : '/static/data/tpls/trip.html',
		replace : true
	};
});

