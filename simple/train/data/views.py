from django.shortcuts import render
import codecs
OFFSET=10
def show_raw_data(req):
    filename = req.GET['file']
    lineno = int(req.GET['line'])
    from_lineno = max(0,lineno-OFFSET)
    to_lineno = (lineno+OFFSET)
    ctx = dict()
    cur_lineno = 1
    lines = []
    file_path = 'parser/unzip_data/%s' % filename
    with codecs.open(file_path,encoding="windows-1255") as fh:
        for line in fh:
            if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                lines.append({'lineno' : cur_lineno,
                              'line' : line.strip().encode('utf-8',errors='ignore')})
            cur_lineno+=1
    ctx['lines'] = lines
    ctx['filename'] = filename
    ctx['lineno'] = lineno
    ctx['prev'] = '/raw-data?file=%s&line=%s' % (filename,lineno-OFFSET*2)
    ctx['next'] = '/raw-data?file=%s&line=%s' % (filename,lineno+OFFSET*2)
    return render(req, 'data/raw_data.html', ctx)

