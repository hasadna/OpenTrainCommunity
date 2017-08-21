angular.module('RouteExplorer')
    .filter('week_day', function () {
        let daysTable = {
            0: 'ראשון',
            1: 'שני',
            2: 'שלישי',
            3: 'רביעי',
            4: 'חמישי',
            5: 'שישי',
            6: 'שבת',
            'all': 'כל הימים'
        };
        return function (day) {
            return daysTable[day] || `??? ${day}`;
        }
    }).filter('hours', function () {
        return function(hours) {
            if (hours == 'all') {
                return 'כל היום'
            }
            return `${hours[0]} - ${hours[1]}`;
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


