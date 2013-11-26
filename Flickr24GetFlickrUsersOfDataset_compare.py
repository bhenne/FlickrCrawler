"""compare two list of user names to find difference

A=user-3k-mobile.txt, B=user-20k-any.txt, A: 3258, B: 20836, onlyA: 3130, onlyB: 20708, both: 128
A=user-3k-mobile.txt, B=user-50k-mobile.txt, A: 3258, B: 50203, onlyA: 2535, onlyB: 49480, both: 723
A=user-3k-mobile.txt, B=user-100k-any.txt, A: 3258, B: 100710, onlyA: 2878, onlyB: 100330, both: 380
A=user-3k-mobile.txt, B=user-54k-mobile.txt, A: 3258, B: 54086, onlyA: 3138, onlyB: 53966, both: 120
A=user-20k-any.txt, B=user-50k-mobile.txt, A: 20836, B: 50203, onlyA: 20483, onlyB: 49850, both: 353
A=user-20k-any.txt, B=user-100k-any.txt, A: 20836, B: 100710, onlyA: 10043, onlyB: 89917, both: 10793
A=user-20k-any.txt, B=user-54k-mobile.txt, A: 20836, B: 54086, onlyA: 20690, onlyB: 53940, both: 146
A=user-50k-mobile.txt, B=user-100k-any.txt, A: 50203, B: 100710, onlyA: 44222, onlyB: 94729, both: 5981
A=user-50k-mobile.txt, B=user-54k-mobile.txt, A: 50203, B: 54086, onlyA: 50203, onlyB: 54086, both: 0
A=user-100k-any.txt, B=user-54k-mobile.txt, A: 100710, B: 54086, onlyA: 98637, onlyB: 52013, both: 2073
"""

files = [ 'user-3k-mobile.txt', 'user-20k-any.txt', 'user-50k-mobile.txt', 'user-100k-any.txt', 'user-54k-mobile.txt']

def compare(filea, fileb):
    a = set()
    f = open(filea, 'rt')
    for line in f:
        a.add(line)
    f.close()
    filea = filea.rpartition('/')[2]

    b = set()
    f = open(fileb, 'rt')
    for line in f:
        b.add(line)
    f.close()
    fileb = fileb.rpartition('/')[2]

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


for filea in files:
    for fileb in files[files.index(filea):]:
        if filea != fileb:
            compare(filea, fileb)
