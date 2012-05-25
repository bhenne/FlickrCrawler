"""This script reads Flickr People from CSV file and loads max. 100 Photo IDs (first page) for each user.

Photos for each user are stored in a CSV file per Person in flickr_photos/. 
For output format of CSV see following code.
"""

import flickr_api       #APICALL (once)
import csv
import codecs
import time
import sys

persons = {}
NSIDs = []

def read_Persons(file='flickr_data/Flickr_users_mobile_unicode.txt'):
    csvReader = csv.reader(open(file, 'rt'), delimiter=';')
    for row in csvReader:
        if len(row) == 1:
            continue
        if row[1] == 'True':
            ispro = True
        else:
            ispro = False
        p = flickr_api.Person(username=row[0], ispro=ispro, realname=row[2],
                              path_alias=row[3], id=row[4], nsid=row[5], location=row[6],
                              p_count=row[7], p_firstdate=row[8], p_firstdatetaken=row[9])
        persons[row[5]] = p
        NSIDs.append(row[5])


read_Persons()

path='flickr_photos_mobile/'
for nsid in NSIDs:
    person = persons[nsid]
    photos = None
    try:
        photos = person.getPublicPhotos()       #APICALL (n times)
    except:
        sys.stderr.write('Error with Person %s' % nsid)
        continue
    time.sleep(1)
    if photos is not None:
        f = codecs.open('%s%s.csv' % (path, nsid.replace('@','-AT-')), 'wt', 'utf-8')
        for photo in photos.data:
            line = u';'.join([ nsid, photo.id, photo.secret, str(photo.farm), str(photo.server), photo.title.replace(';', ',') ])
            f.write(line)
            f.write('\n')
        f.close()
        print flickr_api.method_call.APICOUNTER


print flickr_api.method_call.APICOUNTER
