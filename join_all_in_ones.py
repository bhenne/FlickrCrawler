initdb3 = """CREATE TABLE IF NOT EXISTS all_in_one(
  mobile NUM,
  status INT,
  purl TEXT,
  username TEXT,
  realname TEXT,
  is_pro NUM,
  id TEXT,
  nsid TEXT,
  location TEXT,
  photo_count INT,
  photo_firstdate NUM,
  photo_firstdatetaken NUM,
  photo_id TEXT,
  photo_secret INT,
  photo_farm INT,
  photo_server INT,
  title TEXT,
  json_photo_info TEXT,
  json_photo_exif TEXT,
  url TEXT
);
"""

import sqlite3
import os

dbfile1 = '/mnt/WORKING-ON/50k-mobile/FlickrPhotos.db'
dbfile2 = '/home/henne/flickr/data/FlickrPhoto_onlyMobile_freeze2411.db'
dbfile3 = '/home/henne/flickr/data/FlickrPhoto_onlyMobile_diff2411.db'
filterdir = '/home/henne/flickr/data/m'

copy_db1_content_also_not_just_diff_of_db2 = False

justthisfiles = os.listdir(filterdir)

db1 = sqlite3.connect(dbfile1)
db2 = sqlite3.connect(dbfile2)
db3 = sqlite3.connect(dbfile3)
c1 = db1.cursor()
c2 = db2.cursor()
c3 = db3.cursor()
s1 = set()
s2 = set()

c3.execute(initdb3)

c1.execute('SELECT COUNT(DISTINCT id) FROM all_in_one')
r = c1.fetchone()
print '%s: %s' % (dbfile1, r[0])
c2.execute('SELECT COUNT(DISTINCT id) FROM all_in_one')
r = c2.fetchone()
print '%s: %s' % (dbfile2, r[0])


c1.execute('SELECT DISTINCT id FROM all_in_one')
r = c1.fetchone()
while r is not None:
    s1.add(r[0])
    r = c1.fetchone()


if copy_db1_content_also_not_just_diff_of_db2 == True:
    c1.execute('SELECT mobile, status, purl, username, realname, is_pro, id, nsid, location, photo_count, photo_firstdate, photo_firstdatetaken, photo_id, photo_secret, photo_farm, photo_server, title, json_photo_info, json_photo_exif, url FROM all_in_one')
    r = c1.fetchone()
    while r is not None:
        c3.execute('INSERT INTO all_in_one (mobile, status, purl, username, realname, is_pro, id, nsid, location, photo_count, photo_firstdate, photo_firstdatetaken, photo_id, photo_secret, photo_farm, photo_server, title, json_photo_info, json_photo_exif, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', r)
        r = c1.fetchone()


c2.execute('SELECT mobile, status, purl, username, realname, is_pro, id, nsid, location, photo_count, photo_firstdate, photo_firstdatetaken, photo_id, photo_secret, photo_farm, photo_server, title, json_photo_info, json_photo_exif, url FROM all_in_one')
r = c2.fetchone()
while r is not None:
    person_id = r[6]
    filename = r[19].rpartition('/')[2]
    if person_id in s1 or person_id in s2:
        print 'duplicate %s' % person_id
        r = c2.fetchone()
        continue
    elif filename not in justthisfiles:
        print 'filtered %s' % filename
        r = c2.fetchone()
        continue
    else:
        print 'new %s, %s' % (person_id, filename)
        c3.execute('INSERT INTO all_in_one (mobile, status, purl, username, realname, is_pro, id, nsid, location, photo_count, photo_firstdate, photo_firstdatetaken, photo_id, photo_secret, photo_farm, photo_server, title, json_photo_info, json_photo_exif, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', r)
    s2.add(r[6])
    r = c2.fetchone()
    continue
db3.commit()


c3.execute('SELECT COUNT(DISTINCT id) FROM all_in_one')
r = c3.fetchone()
print '%s: %s' % (dbfile3, r[0])

db1.close()
db2.close()
db3.close()
