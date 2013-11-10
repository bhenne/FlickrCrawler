"""outputs photo owners of new datasets from sqlite data"""

import sqlite3

dbfile = '/Users/henne/research_data/LocrFlickr_datasets2/Flickr/Flickr/50k-mobile/FlickrPhotos.db'

dbconn = sqlite3.connect(dbfile)
dbcursor = dbconn.cursor()

dbcursor.execute('SELECT nsid, username FROM all_in_one')
uid = dbcursor.fetchone()

uids = []
while uid is not None:
    uids.append(uid[0]) #nsid
    #uids.append(uid[1]) #username
    uid = dbcursor.fetchone()

for owner in sorted(uids):
    print owner
