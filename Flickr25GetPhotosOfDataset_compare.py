"""compare two list of photos to find difference

A=photo-3k-mobile.txt, B=photo-20k-any.txt, A: 3258, B: 20836, onlyA: 3144, onlyB: 20722, both: 114
A=photo-3k-mobile.txt, B=photo-50k-mobile.txt, A: 3258, B: 50203, onlyA: 3245, onlyB: 50190, both: 13
A=photo-3k-mobile.txt, B=photo-100k-any.txt, A: 3258, B: 100710, onlyA: 3257, onlyB: 100709, both: 1
A=photo-20k-any.txt, B=photo-50k-mobile.txt, A: 20836, B: 50203, onlyA: 20833, onlyB: 50200, both: 3
A=photo-20k-any.txt, B=photo-100k-any.txt, A: 20836, B: 100710, onlyA: 20464, onlyB: 100338, both: 372
A=photo-50k-mobile.txt, B=photo-100k-any.txt, A: 50203, B: 100710, onlyA: 49901, onlyB: 100408, both: 302
"""

files = [ 'photo-3k-mobile.txt', 'photo-20k-any.txt', 'photo-50k-mobile.txt', 'photo-100k-any.txt' ]

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
