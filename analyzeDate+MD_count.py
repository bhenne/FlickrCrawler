import csv

datafile = '/home/henne/crawl2/crawlerflickr/Date+MD.tsv'

f = open(datafile, 'rt')
tsv = csv.reader(f, delimiter='\t')

all = {}
loc = {}

for row in tsv:
	try:
		year, month, daytime = row[0].split('-')
	except ValueError:
		continue
	if year in all:
		if month in all[year]:
			all[year][month] += 1
		else:
			all[year][month] = 1
	else:
		all[year] = { month : 1 }
	#if row[4] == 'True':	# location
	#if row[5] == 'True':	# location exif
	if row[7] != 'None':	# location exif
        	if year in loc:
                	if month in loc[year]:
                        	loc[year][month] += 1
                	else:
                        	loc[year][month] = 1
        	else:
                	loc[year] = { month : 1 }

for y in sorted(all):
	for m in sorted(all[y]):
		a = all[y][m]
		try:
			l = loc[y][m]
		except:
			l = 0
		print y, m, a, l, 100.0/a*l

for y in sorted(all):
	a = 0
	l = 0
        for m in all[y]:
                a += all[y][m]
                try:
                        l += loc[y][m]
                except:
                        pass
        print y, a, l, 100.0/a*l
