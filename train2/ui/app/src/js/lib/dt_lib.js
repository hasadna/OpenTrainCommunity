export let daysTable = [{
        value: 0,
        name: 'ראשון',
    }, {
        value: 1,
        name: 'שני',
    }, {
        value: 2,
        name: 'שלישי',
    }, {
        value: 3,
        name: 'רביעי',
    }, {
        value: 4,
        name: 'חמישי',
    }, {
        value: 5,
        name: 'שישי',
    }, {
        value: 6,
        name: 'שבת',
    }
    ];

export let monthNames =  [
        'dummy',
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

export let hoursList = [
    {
        name: '4-7',
        values: [4, 5, 6]
    },
    {
        name: '7-9',
        values: [7, 8]
    },
    {
        name: '9-12',
        values: [9,10,11],
    },
    {
        name: '12-15',
        values: [12,13,14],
    },
    {
        name: '15-18',
        values: [15,16,17],
    },
    {
        name: '18-21',
        values: [18, 19,20],
    },
    {
        name: '21-24',
        values: [21, 22,23],
    },
    {
        name: '24-4',
        values: [0, 1, 2, 3],
    }
];

export class TimeParser {
    static createRequestString(date, sep) {
        sep = sep || '/';
        let dd = date.getDate().toString();
        let mm = (date.getMonth()+1).toString();
        let yyyy = date.getFullYear().toString();
        return dd + sep + mm + sep + yyyy;
    }

    static parseMonth(monthString) {
        let year = Number(monthString.substr(0, 4));
        let month = Number(monthString.substr(4, 2));
        return new Date(year, month - 1, 1);
    }

    static parsePeriod(periodString) {
        let parts = periodString.split('-', 2);
        let from = TimeParser.parseMonth(parts[0]);
        let to = parts.length > 1 ? this.parseMonth(parts[1]) : from;
        let end = new Date(to.getFullYear(), to.getMonth() + 1, 1);
        return { from: from, to: to, end: end };
    }

    static formatMonth(date) {
        return date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2);
    }

    static formatPeriod(period) {
        let f = TimeParser.formatMonth(period.from);
        if (period.from < period.to)
            f += '-' + TimeParser.formatMonth(period.to);

        return f;
    }
};





