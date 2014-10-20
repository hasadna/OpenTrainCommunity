from django.shortcuts import render
def show_raw_data(req):
    filename = req.GET['file']
    lineno = int(req.GET['line'])
    from_lineno = max(0,lineno-10)
    to_lineno = (lineno+10)
    ctx = dict()
    cur_lineno = 1
    lines = []
    with open('parser/unzip_data/%s' % filename) as fh:
        for line in fh:
            if cur_lineno >= from_lineno and cur_lineno <= to_lineno:
                lines.append({'lineno' : cur_lineno, 'line' : line.strip()})
            lineno+=1
    ctx['lines'] = lines
    return render(req, 'data/raw_data.html', ctx)

