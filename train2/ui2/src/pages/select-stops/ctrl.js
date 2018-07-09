export default class SelectStopsController {
    constructor($scope, $rootScope, $location, Layout, Locale, TimeParser) {
        'ngInject';
        this.stops = Layout.getStops();
        this.origin = null;
        this.destination = null;
        this.months = Locale.months;

        let dateRange = Layout.getRoutesDateRange();
        this.periods = generatePeriods(dateRange.min, dateRange.max);
        this.startPeriod = this.periods[0];
        this.endPeriod = this.periods[0];

        this.formValid = function () {
            return (
                !!this.origin &&
                !!this.destination &&
                this.origin != this.destination &&
                this.startPeriod.from <= this.endPeriod.to
            );
        };

        this.stopName = function (stopId) {
            var stop = Layout.findStop(stopId);
            if (!stop)
                return null;

            return stop.name;
        };

        this.goToRoutes = function () {
            this.noRoutes = false;
            this.loading = true;
            var period = {
                from: this.startPeriod.from,
                to: this.endPeriod.to,
                end: this.endPeriod.end,
            };
            var fromDate = period.from;
            var toDate = period.end;
            var periodStr = TimeParser.formatPeriod(period);
            Layout.findRoutesByPeriod(this.origin.id, this.destination.id, fromDate, toDate)
                .then(function (routes) {
                    if (routes.length === 0) {
                        this.noRoutes = true;
                    } else if (routes.length == 1) {
                        $location.path('/' + periodStr + '/routes/' + routes[0].id);
                    } else {
                        $location.path('/' + periodStr + '/select-route/' + this.origin.id + '/' + this.destination.id);
                    }
                })
                .finally(function () {
                    this.loading = false;
                });
        };

        this.dismissError = function () {
            this.noRoutes = false;
        };

        function generatePeriods(fromDate, toDate) {
            // fromDate=1970-1-1 due to a data bug. This is a quick temporary workaround
            if (fromDate.getFullYear() < 2013) fromDate = new Date(2013, 0, 1);

            var periods = [];
            var start = new Date(fromDate.getFullYear(), fromDate.getMonth(), 1);
            while (start < toDate) {
                let end = new Date(start.getFullYear(), start.getMonth() + 1, start.getDate());
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
    }
}


