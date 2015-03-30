import requests
import json
import time
import sys
import os

def main(url):
    t1 = time.time()
    r = requests.get(url)
    assert r.ok,'failed in call: %s' % r
    j = r.json()
    t2 = time.time()
    fname = url
    for c in ['://','/','?','&']:
        fname = fname.replace(c,'-')
    fname = os.path.join('output',fname)
    fname = fname + '.json'
    with open(fname,'w') as fh:
        json.dump(j,fh,indent=4)
    print 'Took: %.2f Wrote to %s' % (t2-t1,fname)

if __name__ == '__main__':
    assert len(sys.argv) == 2,'Should be <url>'
    main(sys.argv[1])
