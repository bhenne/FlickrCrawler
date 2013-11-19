"""stats for output of Flickr05AnalyzeMetadata.py with some prior filtering

stats to stdour, filtered data to outfile if not None
"""


import codecs
import csv
import sys

#CSVFILE = 'FlickrDataset-20k-new.txt'
#CSVFILE = 'FlickrDataset-20k-new2.txt'
#CSVFILE = 'FlickrDataset-3k-new.txt'
CSVFILE = 'FlickrDataset-3k-new2.txt'
outfile = CSVFILE.rstrip('.txt') + '_filtered.txt'
#outfile = None

if outfile is not None:
    o = codecs.open(outfile, 'wt', 'utf-8')

def out(line):
    if outfile is not None:
        if not line.endswith('\n') and not line.endswith(u'\u2028'):
            line = line + '\n'
        o.write(line)

header = None
headerlen = 0
brokenrow = []
counts = {}
with codecs.open(CSVFILE, 'rt', 'utf-8') as csvfile:
    for line in csvfile:
        row = line.split(u';')
        if header == None:
            hline = line.strip('#')
            header = row
            header[0] = header[0].strip('#')
            header[-1] = header[0].rstrip('\n')
            out(u";".join(header))
            headerlen = len(header)
            print "fields:", headerlen
            continue
        if len(row) < headerlen:
            # misplaced linebreaks may have broken reading complete line => aggregate
            print "< row len mismatch:", len(row), "\n", row
            brokenrow += row
            print len(brokenrow)
            if len(brokenrow) >= headerlen:
                # now we have a complete aggreagted line according to length
                print "used brokenrow"
                row = brokenrow
                print len(row), "\n", row
                brokenrow = []
            else:
                continue
        if len(row) > headerlen:
            # remove linebreaks within aggregated lines
            print "> row len mismatch:", len(row), "\n", row
            for j in xrange(1, len(row)):
                for i in xrange(1, len(row)):
                    if row[i-1].endswith('\n') or row[i-1].endswith(u"\u2028"):
                        row = row[:max(0, i-1)] + [row[i-1].rstrip('\n').rstrip(u"\u2028") + row[i]] + row[i+1:]
                        break
            if len(row) == headerlen:
                print "fixed line"
        if len(row) != headerlen:
            print "ROW MISMATCH!", len(row)
            continue
        for i in xrange(0, len(row)):
            val = 0

            # remove empty fields only containing quotes
            if row[i].startswith('u"') == True:
                row[i] = row[i].lstrip('u"').rstrip('"')
            if row[i].startswith("'") == True:
                row[i] = row[i].lstrip("'").rstrip("'")
            row[i] = row[i].strip(' ')

            # remove Camera names from description which mostly are in capitals
            try:
                if header[i].find('Description') > -1:
                    if row[i] == row[i].upper():
                        row[i] = ''
            except:
                print i, len(row), len(header), headerlen, row[i], "\n", row
                raise
            
            # replace value 0 with ''
            if header[i] == 'flickr_haspeople':
                try:
                    if int(row[i]) == 0:
                        row[i] = ''
                except ValueError:
                    row[i] = ''

            if len(row[i]) > 0:
                val = 1
            counts[i] = counts.get(i, 0) + val

        row[-1] = row[0].rstrip('\n')
        row[-1] = row[0].rstrip(u"\u2028")

        outline = ";".join(row)
        out(outline)

x = []
for i in xrange(0, len(counts.keys())):
    x.append(str(counts[i]))
    print header[i], '=', counts[i]

print ''
print hline.strip('\n')
print ";".join(x)

