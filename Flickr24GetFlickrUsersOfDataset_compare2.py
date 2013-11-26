"""compare two list of user names to find difference

A=user-20k-any.txt, B=not_user-20k-any.txt, A: 20836, B: 199158, onlyA: 9825, onlyB: 188147, both: 11011
A=user-50k-mobile.txt, B=not_user-50k-mobile.txt, A: 50203, B: 165429, onlyA: 43554, onlyB: 158780, both: 6649
A=user-100k-any.txt, B=not_user-100k-any.txt, A: 100710, B: 126961, onlyA: 82022, onlyB: 108273, both: 18688
A=user-54k-mobile.txt, B=not_user-54k-mobile.txt, A: 54086, B: 157116, onlyA: 51867, onlyB: 154897, both: 2219
A=user-3k-mobile.txt, B=not_user-3k-mobile.txt, A: 3258, B: 206822, onlyA: 2161, onlyB: 205725, both: 1097
"""

files = [ 'user-3k-mobile.txt', 'user-20k-any.txt', 'user-50k-mobile.txt', 'user-100k-any.txt', 'user-54k-mobile.txt' ]

def compare(a, b, filea='', fileb=''):

    both = set()
    onlya = set()
    onlyb = set()

    for x in a:
        if x in b:
            both.add(x)
        else:
            onlya.add(x)

    for x in b:
        if x in a:
            both.add(x)
        else:
            onlyb.add(x)

    print "A=%s, B=%s, A: %s, B: %s, onlyA: %s, onlyB: %s, both: %s" % (filea, fileb, len(a), len(b), len(onlya), len(onlyb), len(both))

contents = {}
for filea in files:
    a = set()
    f = open(filea, 'rt')
    for line in f:
        a.add(line)
    f.close()
    filea = filea.rpartition('/')[2]
    contents[filea] = a

c2 = {}
for name in contents.keys():
    u = set()
    for other in contents.keys():
        if other != name:
            u = u | contents[other]
    c2['not_%s' % name] = u 

for name in contents.keys():
    compare(contents[name], c2['not_%s' % name], filea=name, fileb='not_%s' % name)
