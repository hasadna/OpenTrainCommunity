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
    console.log(r);
    let y = r.getFullYear();
    let m = r.getMonth() + 1;
    let d = r.getDate() + 1;
    return `${d}/${m}/${y}`;
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

const dtUtils = {
    monthNames,
    daysNames,
    getRange,
    computeStart,
    isFullWeek,
    formatHours,
    toDate,
    toHM,
    HMS2HM
};

export default dtUtils;


