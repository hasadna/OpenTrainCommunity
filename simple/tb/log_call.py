import requests
import json
import time
import datetime
import sys
import os

def main(url):
    if not os.path.exists('output'):
        os.mkdir('output')
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    t1 = time.time()
    r = requests.get(url)
    assert r.ok,'failed in call: %s' % r
    j = r.json()
    t2 = time.time()
    base = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    summary = 'output/{0}.summary.json'.format(base)
    output = 'output/{0}.out.json'.format(base)
    if os.path.exists(summary) or os.path.exists(output):
        raise ValueError('{0} Already exists, wait 1 second'.format(summary))
    took = t2 - t1
    jsummary = dict()
    jsummary['output'] = output
    jsummary['url'] = url
    jsummary['rerun'] = "python log_call.py '{0}'".format(url)
    jsummary['time'] = t2 - t1
    with open(summary,'w') as fh:
        json.dump(jsummary,fh,indent=4,sort_keys=True)
    with open(output,'w') as fh:
        json.dump(j,fh,indent=4,sort_keys=True)
    print('Wroute output to {0}'.format(output))
    print('Wrote summary to {0}'.format(summary))

if __name__ == '__main__':
    assert len(sys.argv) == 2,'Should be <url>'
    main(sys.argv[1])
