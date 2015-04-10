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
    infos1_headers = [(info['week_day'],unicode(info['hours'])) for info in infos1]
    infos2_headers = [(info['week_day'],unicode(info['hours'])) for info in infos2]

    infos1_headers_set = set(infos1_headers)
    infos2_headers_set = set(infos2_headers)

    if infos1_headers_set != infos2_headers_set:
        if infos1_headers_set - infos2_headers_set:
            print 'Only in %s:' %f1
            print list(infos1_headers_set - infos2_headers_set)
        if infos2_headers_set - infos1_headers_set:
            print 'Only in %s:' % f2
            print list(infos2_headers_set - infos1_headers_set)
        

    else:
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

