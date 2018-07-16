export default function TimeParser() {
    function createRequestString(date, sep) {
        sep = sep || '/';
        var dd = date.getDate().toString();
        var mm = (date.getMonth()+1).toString();
        var yyyy = date.getFullYear().toString();
        return dd + sep + mm + sep + yyyy;
    }

    function parseMonth(monthString) {
        var year = Number(monthString.substr(0, 4));
        var month = Number(monthString.substr(4, 2));
        return new Date(year, month - 1, 1);
    }

    function parsePeriod(periodString) {
        var parts = periodString.split('-', 2);
        var from = parseMonth(parts[0]);
        var to = parts.length > 1 ? parseMonth(parts[1]) : from;
        var end = new Date(to.getFullYear(), to.getMonth() + 1, 1);
        return { from: from, to: to, end: end };
    }

    function formatMonth(date) {
        return date.getFullYear() + ('0' + (date.getMonth() + 1)).slice(-2);
    }

    function formatPeriod(period) {
        var f = formatMonth(period.from);
        if (period.from < period.to)
            f += '-' + formatMonth(period.to);

        return f;
    }

    return {
        createRequestString: createRequestString,
        parseMonth: parseMonth,
        parsePeriod: parsePeriod,
        formatMonth: formatMonth,
        formatPeriod: formatPeriod
    }
};


