"""compare two list of photos to find difference

A=photo-100k-any.txt, B=not_photo-100k-any.txt, A: 100710, B: 128254, onlyA: 100035, onlyB: 127579, both: 675
A=photo-54k-mobile.txt, B=not_photo-54k-mobile.txt, A: 54086, B: 174203, onlyA: 54086, onlyB: 174203, both: 0
A=photo-3k-mobile.txt, B=not_photo-3k-mobile.txt, A: 3258, B: 225158, onlyA: 3131, onlyB: 225031, both: 127
A=photo-20k-any.txt, B=not_photo-20k-any.txt, A: 20836, B: 207941, onlyA: 20348, onlyB: 207453, both: 488
A=photo-50k-mobile.txt, B=not_photo-50k-mobile.txt, A: 50203, B: 178403, onlyA: 49886, onlyB: 178086, both: 317
"""

files = [ 'photo-3k-mobile.txt', 'photo-20k-any.txt', 'photo-50k-mobile.txt', 'photo-100k-any.txt' , 'photo-54k-mobile.txt']

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
