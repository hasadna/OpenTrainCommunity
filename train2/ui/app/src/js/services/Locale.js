let Locale = {
  months: [
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
  ].map(function(v, i) { return { id: i + 1, name: v }; }),

  days: [
      { abbr: 'א', name: 'ראשון', id: 1 },
      { abbr: 'ב', name: 'שני', id: 2 },
      { abbr: 'ג', name: 'שלישי', id: 3 },
      { abbr: 'ד', name: 'רביעי', id: 4 },
      { abbr: 'ה', name: 'חמישי', id: 5 },
      { abbr: 'ו', name: 'שישי', id: 6 },
      { abbr: 'ש', name: 'שבת', id: 7 }
  ],
  until: 'עד ל'
};

export default Locale;
