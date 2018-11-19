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

const dtUtils = {
    monthNames,
    getRange,
    computeStart
}

export default dtUtils;


