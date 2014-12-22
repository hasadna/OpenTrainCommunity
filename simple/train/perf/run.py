import requests
import json
resp = requests.get('http://localhost:8000/api/route-info/?stop_ids=1600,1500,800,700,1300,1220,2100,2200,2300,2500,2800,2820,3100,3300,3400,3500,3600,3700,4600,4900,8600,300,400')
with open('ref.json') as fh:
    ref = json.load(fh)
    assert ref == resp.json()

print 'OK'



