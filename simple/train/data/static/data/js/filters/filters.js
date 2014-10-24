var myFilters = angular.module('my.filters',[]);

myFilters.filter('filterCount',function() {
	return function(input) {
		if ( input > 0) {
			return '(' + input +')';
		} else {
			return '';
		}
	};
});

myFilters.filter('nothingIfZero',function() {
	return function(input,sep) {
		if ( input > 0) {
			return input + sep;
		} else {
			return '';
		}
	};
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

myFilters.filter('na',function() {
	return function(input) {
	    if (input) {
		return input;
	    } else {
		return 'NA';
	    }
	};
});


myFilters.filter('splitn',function() {
	return function(input) {
		return input.split(/\n/g);
	};
});

myFilters.filter('toString',function() {
	return function(input) {
		return input.toString();
	};
});

myFilters.filter('joinList',function() {
	return function(input) {
		if (!input) {
			return '';
		};
		return input.join(',');
	};
});

myFilters.filter('blankIfNull',function() {
	return function(input) {
		if (!input) {
			return '';
		}
		return input;
	};
});

myFilters.filter('spaceList',function() {
	return function(input) {
		if (!input) {
			return '';
		}
		return input.join(" ");
	};
});

myFilters.filter('spaceListParen',function() {
	return function(input) {
		if (!input) {
			return '';
		}
	    input = input.map(function(it) {
		return '"' + it + '"';
	    });
		return input.join(" ");
	};
});

myFilters.filter('toDate',function() {
	return function(input) {
		return new Date(input);
	};
});

myFilters.filter('ago',function() {
	return function(input) {
		// pass null for the current time
		var delta = {
				printUnitsPlural : function(num,unit) {
					if (num > 1) {
						return num + ' ' + unit + 's';
					} else {
						return num + ' ' + unit; 
					};
				}
		};
		var early = new Date(input);
		var late = new Date();
		var secsLeft = Math.floor((late.getTime() - early.getTime()) / 1000);
		delta.days = Math.floor(secsLeft / (60 * 60 * 24));
		secsLeft = secsLeft - delta.days * 60 * 60 * 24;
		delta.hours = Math.floor(secsLeft / (60 * 60));
		secsLeft = secsLeft - delta.hours * 60 * 60;
		delta.minutes = Math.floor(secsLeft / 60);
		delta.seconds = secsLeft - delta.minutes * 60;

		if (delta.days > 0) {
			return delta.printUnitsPlural(delta.days, 'day') + ' ago';
		}
		// if in hours, we return hours + minutes
		if (delta.hours > 0) {
			return delta.printUnitsPlural(delta.hours, 'hour') + ' and '
					+ delta.printUnitsPlural(delta.minutes, 'minute') + ' ago';
		}
		if (delta.minutes > 0) {
			return delta.printUnitsPlural(delta.minutes, 'min') + ' ago';
		}
		if (delta.seconds >= 0) {
			return delta.printUnitsPlural(delta.seconds, 'second') + ' ago';
		}
		return 'sometime...';
	};
});

myFilters.filter('tsAgo',function() {
   return function(ts) {
       var late = new Date();
       var secsLeft = Math.floor((late.getTime() - ts*1000) / 1000);
       return secsLeft + ' secs ago';
   };
});

myFilters.filter('tsToTime',function() {
   return function(ts) {
   		var dt = new Date(ts*1000);
       	return dt.toString();
   };
});

myFilters.filter('newlines', function () {
    return function(text) {
        return text.replace(/\n/g, '<br/>');
    };
});

myFilters.filter('noHTML', function () {
    return function(text) {
        return text
                .replace(/&/g, '&amp;')
                .replace(/>/g, '&gt;')
                .replace(/</g, '&lt;');
    };
});

myFilters.filter('show2',function() {
	return function(text) {
		return text.substring(0,20);		
	};
});

myFilters.filter('show50',function() {
	return function(text) {
		if (text.length > 50) {
			return text.substring(0,50) + '...';
		} else {
			return text;
		}	
	};
});

myFilters.filter('reverse',function() {
	return function(arr) {
		if (arr) {
			return arr.slice().reverse();
		} else {
			return arr;
		}
	};
});

myFilters.filter('title',function() {
	return function(name) {
		return name.replace(/_/g,' ').replace(/\w+/g,function(txt) {
			return txt.charAt(0).toUpperCase() + txt.substr(1);
		});
	};
});




