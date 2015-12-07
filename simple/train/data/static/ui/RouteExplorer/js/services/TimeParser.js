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

    return {
        parseMonth: parseMonth,
        parsePeriod: parsePeriod
    }
}]);
