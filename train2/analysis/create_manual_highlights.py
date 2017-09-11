import json


late_highlights = []
ontime_highlights = []
all_highlights = {'late': late_highlights, 'ontime': ontime_highlights}

def createHighlight(url, text):
  highlight = {}
  highlight["url"] = url
  highlight["text"] = text
  return highlight

url = "http://otrain.org/#/201707/routes/124?time=15-18"
text = "1בדיקה בדיקה בדיקה"
late_highlights.append(createHighlight(url, text))

url = "http://otrain.org/#/201707/routes/124?day=1"
text = "2בדיקה בדיקה בדיקה"
late_highlights.append(createHighlight(url, text))

url = "http://otrain.org/#/201707/routes/124?day=1"
text = "3בדיקה בדיקה בדיקה"
late_highlights.append(createHighlight(url, text))

url = "http://otrain.org/#/201707/routes/124?time=15-18"
text = "4בדיקה בדיקה בדיקה"
ontime_highlights.append(createHighlight(url, text))

url = "http://otrain.org/#/201707/routes/124?time=15-18"
text = "5בדיקה בדיקה בדיקה"
ontime_highlights.append(createHighlight(url, text))

url = "http://otrain.org/#/201707/routes/124?day=1"
text = "6בדיקה בדיקה בדיקה"
ontime_highlights.append(createHighlight(url, text))

with open('static/analysis/manual_highlights.json', 'w') as outfile:
  json.dump(all_highlights, outfile)