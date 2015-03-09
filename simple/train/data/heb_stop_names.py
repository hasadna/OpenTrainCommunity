# -*- coding: utf-8 -*-

HEB_NAMES = {
    3700: ["תל אביב סבידור מרכז", 'ת"א סבידור מרכז']
}

for k, v in HEB_NAMES.iteritems():
    assert isinstance(k, int), 'for k = %s key must be integer' % k
    assert isinstance(v, list), 'for k = %s value must be list of string' % k

