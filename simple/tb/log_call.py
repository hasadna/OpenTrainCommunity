import requests
import json
import time
import datetime
import sys
import os

def main(url):
    timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    t1 = time.time()
    r = requests.get(url)
    assert r.ok,'failed in call: %s' % r
    j = r.json()
    t2 = time.time()
    fname = url
    for c in ['://','/','?','&']:
        fname = fname.replace(c,'-')
    fname = os.path.join('output',fname)
    took = t2 - t1
    fname = '%s_%s_%.2f.json' % (fname,timestamp,took)
    with open(fname,'w') as fh:
        json.dump(j,fh,indent=4)
    print 'Took: %.2f Wrote to %s' % (took,fname)

if __name__ == '__main__':
    assert len(sys.argv) == 2,'Should be <url>'
    main(sys.argv[1])
