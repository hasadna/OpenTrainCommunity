import requests
import json
import time
import sys

def check(url, reffile,ext):
    if ext:
        server = '104.131.88.144'
        reffolder = 'ext'
    else:
        server = 'localhost:8000'
        reffolder = 'local'
    t1 = time.time()
    final_url = 'http://%s%s' % (server,url)
    resp = requests.get(final_url)
    t2 = time.time()
    cur = resp.json()
    with open('cur/%s' % reffile,'w') as fh:
        json.dump(cur,fh)
    with open('%s/%s' % (reffolder,reffile)) as fh:
        ref = json.load(fh)
        result = ref == cur
    print '%s %s Took %.3f seconds' % ('OK' if result else 'DIFF',final_url,t2-t1)

    
def run(ext):
    check('/api/all-routes','all_routes.json',ext=ext)
    check('/api/route-info/?stop_ids=1600,1500,800,700,1300,1220,2100,2200,2300,2500,2800,2820,3100,3300,3400,3500,3600,3700,4600,4900,8600,300,400','route_info.json',ext=ext)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--ext',action='store_true')
    ns = parser.parse_args()

    run(ns.ext)



