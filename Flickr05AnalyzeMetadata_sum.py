"""stats for output of Flickr05AnalyzeMetadata.py with some prior filtering

stats to stdour, filtered data to outfile if not None
"""


import codecs
import csv
import sys

CSVFILE = 'FlickrDataset-20k-new.txt'
#CSVFILE = 'FlickrDataset-20k-new2.txt'
#CSVFILE = 'FlickrDataset-3k-new.txt'
#CSVFILE = 'FlickrDataset-3k-new2.txt'
outfile = CSVFILE.rstrip('.txt') + '_filtered.txt'
#outfile = None

if outfile is not None:
    o = codecs.open(outfile, 'wt', 'utf-8')

def out(line):
    if outfile is not None:
        o.write(line)

header = None
counts = {}
with codecs.open(CSVFILE, 'rt', 'utf-8') as csvfile:
    for line in csvfile:
        row = line.split(u';')
        if header == None:
            hline = line.strip('#')
            header = row
            header[0] = header[0].strip('#')
            header[-1] = header[0].rstrip('\n')
            out(";".join(header))
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
            if header[i].find('Description') > -1:
                if row[i] == row[i].upper():
                    row[i] = ''
            
            # replace value 0 with ''
            if header[i] == 'flickr_haspeople':
                if int(row[i]) == 0:
                    row[i] = ''

            if len(row[i]) > 0:
                val = 1
            counts[i] = counts.get(i, 0) + val

        out(";".join(row))

x = []
for i in xrange(0, len(counts.keys())):
    x.append(str(counts[i]))
    print header[i], '=', counts[i]

print ''
print hline.strip('\n')
print ";".join(x)

