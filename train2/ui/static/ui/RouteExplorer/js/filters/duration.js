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
