import requests
import pytz
import datetime
import uuid
import logging
import os
import json
import gzip
import xml.dom.minidom

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s", datefmt="%d/%b/%Y %H:%M:%S")
logger = logging.getLogger(__name__)

utc_tz = pytz.utc
il_tz = pytz.timezone('Asia/Jerusalem')

CUR_DIR = os.path.dirname(__file__)

with open(os.path.join(CUR_DIR, './local_defs.json')) as fh:
    defs = json.load(fh)


base_url = defs['base_url']
username = defs['username']

def get_now():
    return utc_tz.localize(datetime.datetime.utcnow()).astimezone(il_tz).replace(microsecond=0)

def make_request_and_dump():
    now = get_now()
    resp = make_request(now)
    resp.raise_for_status()
    resp_text = resp.text
    y = now.strftime('%Y')
    m = now.strftime('%m')
    d = now.strftime('%d')
    nu = now.strftime('%Y_%m_%d_%H_%M_%S')
    path = os.path.join(CUR_DIR, f'./siri_resps/{y}/{m}/{d}/{nu}.xml.gz')
    pretty_path = os.path.join(CUR_DIR, f'./siri_resps/{y}/{m}/{d}/{nu}_pretty.xml')
    path_dir = os.path.dirname(path)
    os.makedirs(path_dir, exist_ok=True)
    with gzip.open(path,'wt', encoding='utf-8') as fh:
        fh.write(resp_text)
    logger.info('Wrote to %s', path)
    xml_dom = xml.dom.minidom.parseString(resp_text)
    nice_xml = xml_dom.toprettyxml()
    with open(pretty_path, 'w') as fh:
        fh.write(nice_xml)
    logger.info('Wrote pertty xml to %s', pretty_path)    
        
def make_request(now=None):
    now = now or get_now()
    xml = get_xml(now)
    r = requests.post(base_url, data=xml, headers={'Content-Type':'text/xml'})
    logger.info('Called %s => %d', base_url, r.status_code)
    return r

stop_ids = [17042,17046,17120,17117,17008,17010,17012,17014,17016,17018,17022,17024,17026,17028,17030,17032,17034,17036,17040,17044,17048,17050,17052,17054,17056,17104,17058,17060,17108,17002,17038,17062,17064,17066,17068,17070,17004,17117,17123,17121,17122,17072,17074,17078,17080,17084,17086,17088,17090,17092,17094,17096,17098,17100,17106,17102,17020,17000,17109,17113,17110,17114,17111,17112,17116,17115,17119,17118,17082,17076]

def get_req(ts, index, stop_id):
    return '''<siri:StopMonitoringRequest version="2.7">
    <siri:RequestTimestamp>{ts}</siri:RequestTimestamp>
    <siri:MessageIdentifier>{index}</siri:MessageIdentifier>
    <siri:PreviewInterval>PT90M</siri:PreviewInterval>
    <siri:StartTime>{ts}</siri:StartTime>
    <siri:MonitoringRef>{stop_id}</siri:MonitoringRef>
    <siri:MaximumStopVisits>100</siri:MaximumStopVisits>
    </siri:StopMonitoringRequest>'''.format(stop_id=stop_id, index=index,ts=ts)

def get_xml(now):
    ts = now.isoformat()
    mid = str(uuid.uuid4())
    reqs = "\n".join([get_req(ts, index, stop_id) for index, stop_id in enumerate(stop_ids)])
    xml = '''<?xml version="1.0" ?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
	<S:Body>
		<siriWS:GetStopMonitoringService xmlns:siriWS="http://new.webservice.namespace" xmlns="" xmlns:ns4="http://www.ifopt.org.uk/ifopt" xmlns:ns3="http://www.ifopt.org.uk/acsb" xmlns:siri="http://www.siri.org.uk/siri">
			<Request>
				<siri:RequestTimestamp>{ts}</siri:RequestTimestamp>
				<siri:RequestorRef>{username}</siri:RequestorRef>
				<siri:MessageIdentifier>{mid}</siri:MessageIdentifier>
				{reqs}
			</Request>
		</siriWS:GetStopMonitoringService>
	</S:Body>
</S:Envelope>'''.format(ts=ts, username=username,mid=mid, reqs=reqs)
    return xml

    
if __name__ == '__main__':
    make_request_and_dump()

