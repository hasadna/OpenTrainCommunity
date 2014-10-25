var myFilters = angular.module('my.filters',[]);

myFilters.filter('toMinSec',function() {
	return function(input) {
	    function toMinSecPos(secs) {
            if (secs == 0) {
                return '0:00';
            } else if (secs > 0) {
                var m = Math.floor(secs/60)
                var s = Math.floor(secs - m * 60);
                if (s < 10) {
                    s = '0' + s.toString();
                }
                return m + ':' + s;
            }
    	};
	    if (input < 0) {
	        return '-' + toMinSecPos(-input) + ' min';
	    }
	    return toMinSecPos(input) + ' min';
	}
});

myFilters.filter('yesNo',function() {
	return function(input) {
	    if (input) {
		return 'Yes';
	    } else {
		return 'No';
	    }
	};
});

myFilters.filter('toPrec',function() {
	return function(input) {
	    return input * 100;
	};
});


myFilters.filter('hmOnly',function() {
	return function(input) {
	    function to2(d) {
	        return d > 10 ? '' + d : '0' + d;
	    }
	    if (!input) {
	        return '----';
	    }
		var d = new Date(input);
        return '' + to2(d.getHours()) + ':' + to2(d.getMinutes())
	};
});

