let daysTable = {
            0: 'ראשון',
            1: 'שני',
            2: 'שלישי',
            3: 'רביעי',
            4: 'חמישי',
            5: 'שישי',
            6: 'שבת',
        };

angular.module('RouteExplorer')
    .filter('week_day1', function () {
        return function (day) {
            if (day == 'all') {
                return 'כל הימים';
            }
            return daysTable[day-1] || `??? ${day}`;
        }
    }).filter('week_day0', function () {
        return function (day) {
            if (day == 'all') {
                return 'כל הימים';
            }
            return daysTable[day] || `??? ${day}`;
        }
    }).filter('hours', function () {
        return function(hours) {
            let fix = h => h >= 24 ? h % 24 : h;
            if (hours == 'all') {
                return 'כל היום'
            }
            let h1 = fix(hours[1]);
            let h0 = fix(hours[0]);
            return `${h1} - ${h0}`;
        }
    }).filter('month_name', function() {
        let months = [
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
        ]
        return function(m) {
            return months[m-1];
        }
    });


