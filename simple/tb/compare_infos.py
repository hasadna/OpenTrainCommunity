import json
import sys


def extract_infos(f):
    with open(f) as fh:
        data = json.load(fh)
    infos = [e['info'] for e in data]
    return infos
    
def main(f1,f2):
    infos1 = extract_infos(f1)
    infos2 = extract_infos(f2)
    print '%s: %s infos' % (f1,len(infos1))
    print '%s: %s infos' % (f2,len(infos2))
    assert len(infos1) == len(infos2)
    for idx in range(len(infos1)):
        info1 = infos1[idx]
        info2 = infos2[idx]
        assert info1['week_day'] == info2['week_day']
        assert info1['hours'] == info2['hours']
        if info1['num_trips'] != info2['num_trips']:
            print '======================================'
            print 'mismatch:'
            print info1
            print info2



if __name__ == '__main__':
    main(sys.argv[1],sys.argv[2])

