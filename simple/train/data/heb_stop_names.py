# -*- coding: utf-8 -*-

HEB_NAMES = {
    3700: [u"תל אביב סבידור מרכז", u'ת"א סבידור מרכז'],
    3600: [u'תל אביב אוניברסיטה', u'ת"א אוניברסיטה'],
    8600: [u'נתב"ג', u'נמל תעופה בן-גוריון'],
    4600: [u'תל אביב השלום', u'ת"א השלום']
}

for k, v in HEB_NAMES.iteritems():
    assert isinstance(k, int), 'for k = %s key must be integer' % k
    assert isinstance(v, list), 'for k = %s value must be list of string' % k

