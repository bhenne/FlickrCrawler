"""outputs photos of new datasets from sqlite data"""

import sqlite3

dbfile = '/Users/henne/research_data/LocrFlickr_datasets2/Flickr/Flickr/50k-mobile/FlickrPhotos.db'

dbconn = sqlite3.connect(dbfile)
dbcursor = dbconn.cursor()

dbcursor.execute('SELECT url FROM all_in_one')
pid = dbcursor.fetchone()

pids = []
while pid is not None:
    pids.append(pid[0].rpartition('/')[2])
    pid = dbcursor.fetchone()

for photo in sorted(pids):
    print photo
