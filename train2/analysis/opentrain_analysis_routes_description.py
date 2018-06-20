"""Functions to help in analysis of website data using ipython notebook"""
import collections
import json
import os
import requests

SERVER_DOMAIN = 'otrain.org'
LOCAL_DOMAIN = '127.0.0.1:8000'
DOMAIN = SERVER_DOMAIN

def get_stops():
  """Return a list stops from the website API"""
  all_stops = json.loads(requests.get('http://otrain.org/api/v1/stops').text)
  result = {}
  for stop_info in all_stops:
    result.update({stop_info['stop_id']: [stop_info['heb_stop_names'][0], stop_info['stop_name']]})
  return result

def get_hebrew_description(origin, destination, highlight, stop_id_to_name):
  month = "חודש "
  heb_to = " ל"
  everyday_heb = " כל יום "
  aleph = "א"
  bet = "ב"
  gimel = "ג"
  daled = "ד"
  hey = "ה"
  vav = "ו"
  shabbat = "ש"
  days = ["stub", aleph, bet, gimel, daled, hey, vav, shabbat]
  between_hours = "בין השעות "
  delays = " ממוצע איחורים:"
  max_delay = " איחור מקסימאלי:"
  last_stop_delay = " איחור בתחנה אחרונה:"
  day_heb = "" if highlight["week_day"] == 'all' else days[highlight["week_day"]] + " "
  hours_heb = "" if highlight["hours"] == 'all' else between_hours + str(highlight["hours"][0]) + "-" + str(highlight["hours"][1])
  result = str(highlight["month"]) + "/" + str(highlight["year"]) + ": " + stop_id_to_name[origin] + heb_to + stop_id_to_name[destination]
  result += "<br>" + everyday_heb + day_heb + hours_heb
  result += "<br>" + delays + " {0:.0f}%".format(highlight['mean_arrival_late_pct'] * 100)
  result += "<br>" + max_delay + " {0:.0f}%".format(highlight['max_arrival_late_pct'] * 100)
  result += "<br>" + last_stop_delay + " {0:.0f}%".format(highlight['last_stop_arrival_late_pct'] * 100)
  return result

def get_stops_ids_to_heb_name(all_stops):
  """Return a list stop ids from the website API"""
  result = {}
  for stop_info in all_stops:
    result[stop_info['stop_id']] = stop_info['stop_short_name']
  return result

def save_highlights_html(data, stop_id_to_name, filepath):
  count = 1
  with open(filepath, 'w') as html_file:  
    html_file.write('<!DOCTYPE html><html><body dir="rtl">')
    html_file.write('<h1 dir="ltr">Highlights</h1>')
    data = sorted(data, key=lambda highlight: highlight['mean_arrival_late_pct'], reverse=True)
    for highlight in data:
      html_file.write('<h3>{}</h3>'.format(count))
      count += 1
      url = highlight['url']
      if url.endswith('time='):
        url = url[:-5]
      if url.endswith('day='):
        url = url[:-4]
      if url.endswith('&'):
        url = url[:-1]
      if url.endswith('time='):
        url = url[:-5]
      if url.endswith('day='):
        url = url[:-4]
      if url.endswith('?'):
            url = url[:-1]
      html_file.write('<span>{}</span><p>'.format(get_hebrew_description(highlight["first_stop"], highlight["last_stop"], highlight, stop_id_to_name)))
      html_file.write('<a href="{}" target="_blank">{}</a><p>'.format(url, url))
#{'num_trips': 44, 'week_day': 'all', 'url': 'http://otrain.org/#/201706/routes/2439?day=&time=', 'hours': 'all', 'mean_arrival_late_pct': 0.0669191919, 'route_id': 2439, 'month': 6, 'year': 2017}
    html_file.write('</body></html>')


all_stops = json.loads(requests.get('http://{}/api/v1/stops'.format(DOMAIN)).text)
stop_id_to_name = get_stops_ids_to_heb_name(all_stops)
path = "static/analysis/routes_output_format_records.json"
with open(path) as fh:
  data = [json.loads(line) for line in fh]
save_highlights_html(data, stop_id_to_name, 'highlights.html')
