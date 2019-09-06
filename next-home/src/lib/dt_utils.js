import _ from 'lodash';

const daysNames = [
    'ראשון',
    'שני',
    'שלישי',
    'רביעי',
    'חמישי',
    'שישי',
    'שבת',
];

const monthNames = [
    '',
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
    'דצמבר',
];

const shortMonthNames = [
    '',
    'ינו',
    'פבר',
    'מרץ',
    'אפר',
    'מאי',
    'יוני',
    'יולי',
    'אוג',
    'ספט',
    'אוק',
    'נוב',
    'דצמ',
];

let engPrefixes = [
    '',
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec',
]

function isFullWeek(days) {
    if (days && days.length >= 7) {
        for (let i = 0; i <= 6; i++) {
            if (!days.includes(i)) {
                return false;
            }
        }
        return true;
    }
    return false;
}

function computeStart(l, months) {
    let [ly, lm] = l;
    let m1 = ly * 12 + lm - 1;
    let m2 = m1 - (months - 1);
    let sm = 1 + m2 % 12;
    let sy = (m2 - m2 % 12) / 12;
    return [sy, sm]
}

function getRange(s, e) {
    // s: start (y,m)
    // e: end (y,m)
    // return range of pairs from end to start (desc)

    let result = [];
    let [sy, sm] = s;
    let [ey, em] = e;
    let [cy, cm] = [sy, sm];
    while (cy != ey || cm != em) {
        result.push([cy, cm]);
        cm++;
        if (cm == 13) {
            cm = 1;
            cy++;
        }
    }
    result.push([ey, em]);
    result.reverse();
    return result;
}

function formatHours(hours) {
    hours = _.sortBy(hours);
    let pairs = [];
    let curStart = null;
    let curEnd = null;
    for (let h of hours) {
        if (curEnd !== null && h == curEnd+1) {
            curEnd = h;
        } else {
            if (curStart !== null) {
                pairs.push([curStart, curEnd]);
            }
            curStart = h;
            curEnd = h;
        }
    }
    pairs.push([curStart, curEnd]);
    let pairsStrs = pairs.map(p => p[0] === p[1] ? p[0] : `${p[0]}-${p[1]}`);
    return pairsStrs.join(",");
}

function to2(x) {
    if (x < 10) {
        return `0${x}`;
    }
    return x;
}

function toDate(s) {
    let r = new Date(s);
    let y = r.getFullYear();
    let m = r.getMonth() + 1;
    let d = r.getDate();
    return `${d}/${m}/${y}`;
}

function toFreqStr(s, freq) {
    let r = new Date(s);
    r.setHours(12); // make it middle of day, to avoid day time issues
    if (freq === 'w') {
        r.setDate(r.getDate()-r.getDay());
    } else if (freq === 'm') {
        r.setDate(1);
    }
    let y = r.getFullYear();
    let m = to2(r.getMonth() + 1);
    let d = to2(r.getDate());
    return `${y}-${m}-${d}`;
}

function dateStrToMidDay(s) {
    // s if format yyyy-mm-dd
    let [y, m, d] = s.split("-");
    return new Date(parseInt(y), parseInt(m)-1, parseInt(d), 12);
}

function toHM(s) {
    let r = new Date(s);
    let hh = to2(r.getHours());
    let mm = to2(r.getMinutes());
    return `${hh}:${mm}`
}

function HMS2HM(hms) {
    if (hms) {
        return hms.substr(0, 5);
    }
    return ''
}

function engToNumber(n) {
    let nl = n.toLowerCase();
    for (let i = 1; i <= 12 ; i++) {
        let prefix = engPrefixes[i];
        if (nl.startsWith(prefix)) {
            return i;
        }
    }
    return 0;
}


const dtUtils = {
    monthNames,
    shortMonthNames,
    daysNames,
    getRange,
    computeStart,
    isFullWeek,
    formatHours,
    toDate,
    toHM,
    HMS2HM,
    toFreqStr,
    dateStrToMidDay,
    engToNumber,
};

export default dtUtils;


