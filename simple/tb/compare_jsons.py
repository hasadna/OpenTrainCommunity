import json
import sys


def get_json(fname):
    return json.load(open(fname))
    
def main(f1,f2):
    j1 = get_json(f1)
    j2 = get_json(f2)
    deep_cmp(j1,j2)

def cmp_values(v1,v2):
    if isinstance(v1,float):
        ok = abs(v1-v2) < 0.001
    else:
        ok = v1 == v2
    assert ok,'%s and %s are different' % (v1,v2)

def deep_cmp(v1,v2):
    assert type(v1) == type(v2)
    if isinstance(v1,list):
        cmp_lists(v1,v2)
    elif isinstance(v1,dict):
        cmp_dicts(v1,v2)
    else:
        cmp_values(v1,v2)

def cmp_lists(l1,l2):
    assert len(l1) == len(l2)
    for x in range(0,len(l1)):
        deep_cmp(l1[x],l2[x])

def cmp_dicts(d1,d2):
    ok = set(d1.keys()) == set(d2.keys())
    if not ok:
        import pdb
        pdb.set_trace()
    assert ok,'%s vs. %s' % (d1.keys(),d2.keys())
    for k in d1.keys():
        deep_cmp(d1[k],d2[k])


if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])

