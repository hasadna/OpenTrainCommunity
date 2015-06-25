# -*- coding: utf-8 -*-

HEB_NAMES = {
    300: [u'מודיעין'], #  Modiin
    400: [u'מודיעין מרכז'], #  Modiin Center
    700: [u'קריית חיים', u'חיפה קריית חיים'], #  Kiryat Hayyim
    800: [u'קריית מוצקין', u'מוצקין'], #  Kiryat Motzkin
    1220: [u'לב המפרץ', u'חיפה לב המפרץ'], #  Leb Hmifratz
    1300: [u'חוצות המפרץ', u'חיפה חוצות המפרץ'], #  Hutsot HaMifrats
    1500: [u'עכו'], #  Akko
    1600: [u'נהריה'], #  Nahariyya
    2100: [u'חיפה מרכז השמונה', u'מרכז השמונה'], #  Haifa Center HaShmona
    2200: [u'חיפה בת גלים', u'בת גלים'], #  Haifa Bat Gallim
    2300: [u'חיפה חוף הכרמל רזיאל', u'חיפה חוף הכרמל', u'חוף הכרמל', u'רזיאל'], #  Haifa Hof HaKarmel (Razi'el)
    2500: [u'עתלית'], #  Atlit
    2800: [u'בנימינה'], #  Binyamina
    2820: [u'קיסריה - פרדס חנה', u'קיסריה', u'פרדס חנה', u'קיסריה פרדס חנה'], #  Kesariyya - Pardes Hanna
    3100: [u'חדרה מערב'], #  Hadera West
    3300: [u'נתניה'], #  Natanya
    3400: [u'בית יהושוע', u'בית יהושע'], #  Bet Yehoshua
    3500: [u'הרצליה'], #  Herzliyya
    3600: [u'תל אביב אוניברסיטה', u'ת"א אוניברסיטה', u'אוניברסיטת ת"א', u'אוניברסיטת תל אביב'], #  Tel Aviv - University
    3700: [u"תל אביב סבידור מרכז", u'ת"א סבידור מרכז', u'מרכז', u'סבידור', u'סבידור מרכז'], #  Tel Aviv Center - Savidor
    4100: [u'בני ברק'], #  Bne Brak
    4170: [u'פתח תקוה קריית אריה', u'פתח תקווה קריית אריה', u'פתח תקוה קרית אריה', u'פתח תקווה קרית אריה', u'קריית אריה', u'קרית אריה'], #  Petah Tikva   Kiryat Arye
    4250: [u'פתח תקוה סגולה', u'פתח תקווה סגולה', u'סגולה'], #  Petah Tikva Sgulla
    4600: [u'תל אביב השלום', u'ת"א השלום', u'השלום'], #  Tel Aviv HaShalom
    4640: [u'צומת חולון'], #  Holon Junction
    4660: [u'חולון וולפסון', u'חולון ולפסון', u'ולפסון', u'וולפסון'], #  Holon - Wolfson
    4680: [u'בת ים יוספטל', u'יוספטל', u'בת-ים יוספטל'], #  Bat Yam - Yoseftal
    4690: [u'בת ים קוממיות', u'בת-ים קוממיות', u'קוממיות'], #  Bat Yam - Komemiyyut
    4800: [u'כפר חבד', u'כפר חב"ד'], #  Kfar Habbad
    4900: [u'תל אביב ההגנה', u'ת"א ההגנה', u'ההגנה'], #  Tel Aviv HaHagana
    5000: [u'לוד'], #  Lod
    5010: [u'רמלה'], #  Ramla
    5150: [u'גני אביב', u'לוד גני אביב'], #  Ganey Aviv
    5200: [u'רחובות הדר', u'הדר רחובות', u'רחובות'], #  Rehovot E. Hadar
    5300: [u'באר יעקוב', u'באר יעקב', u'באר-יעקוב', u'באר-יעקב'], #  Be'er Ya'akov
    5410: [u'יבנה'], #  Yavne
    5800: [u'אשדוד', u'עד הלום', u'עד-הלום', u'אשדוד עד-הלום', u'אשדוד עד הלום'], #  Ashdod Ad Halom
    5900: [u''], #  Ashkelon
    6300: [u''], #  Bet Shemesh
    6500: [u'', u'', u'', u''], #  Jerusalem Biblical Zoo
    6700: [u'', u''], #  Jerusalem Malha
    7000: [u''], #  Kiryat Gat
    7300: [u'', u'', u'', u''], #  Be'er Sheva North University
    7320: [u''], #  Be'er Sheva Center
    7500: [u''], #  Dimona
    8550: [u'', u'', u''], #  Lehavim - Rahat
    8600: [u'נתב"ג', u'נמל תעופה בן-גוריון', u''], #  Ben Gurion Airport
    8700: [u''], #  Kfar Sava
    8800: [u'', u''], #  Rosh Ha'Ayin North
    9000: [u''], #  Yavne - West
    9100: [u'', u'', u''], #  Rishon LeTsiyyon HaRishonim
    9200: [u''], #  Hod HaSharon
    9600: [u''], #  Sderot
    9800: [u'', u'', u''], #  Rishon LeTsiyyon - Moshe Dayan
}


for k, v in HEB_NAMES.iteritems():
    assert isinstance(k, int), 'for k = %s key must be integer' % k
    assert isinstance(v, list), 'for k = %s value must be list of string' % k

