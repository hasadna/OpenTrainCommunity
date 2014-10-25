"use strict";
var services = angular.module('my.services', ['my.filters']);

services.factory('MyHttp', ['$http',
function($http) {
	var doHttp = function(method, conf) {
		method = method.toUpperCase();
		var headers = {};
		var httpConfig = {
			method : method,
			url : conf.url,
			data : conf.data,
			params : conf.params,
			headers : headers
		};
		return $http(httpConfig).error(function(data, status, headers, config) {
		    alert('failed in ' + config.url + '\n' + status + '\n' + JSON.stringify(data));
		});
	};
	var service = {
		get : function(url, params, conf) {
			conf = conf || {};
			conf.params = params;
			conf.url = url;
			return doHttp('get', conf);
		},
		post : function(url, data, conf) {
			conf = conf || {};
			conf.data = data;
			conf.url = url;
			return doHttp('post', conf);
		},
		postForm : function(url, data, conf) {
			conf = conf || {};
			conf.data = data;
			conf.asForm = true;
			conf.url = url;
			return doHttp('post', conf);
		},
		'delete' : function(url, params, conf) {
			conf = conf || {};
			conf.url = url;
			conf.params = params;
			return doHttp('delete', conf);
		},
		put : function(url, data, conf) {
			conf = conf || {};
			conf.url = url;
			conf.data = data;
			return doHttp('put', conf);
		}
	};
	return service;
}]);

services.controller('TripController', ['$scope', 'MyHttp',
    function($scope, MyHttp) {
        if ($scope.tid) {
            MyHttp.get('/api/trips/' + $scope.tid + '/').success(function(data) {
                $scope.trip = data;
                $scope.expand = false;
            });
        };
    }]);

