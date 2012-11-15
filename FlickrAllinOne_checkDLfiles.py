#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os
from FlickrAllinOne import download_file
import urllib
import shutil
import mimetypes
import sys


#dbfile = '/home/henne/crawled_data/Flickr/FlickrPhotos.db'
dbfile = '/home/henne/crawled_data/Flickr/FlickrPhoto_onlyMobile.db'
photo_file_path = '/home/henne/crawled_data/Flickr'


dbconn = sqlite3.connect(dbfile)

dbcursor = dbconn.cursor()
fileset = set()
fileset2 = set()
for row in dbcursor.execute('SELECT url FROM photo_urls'):
  filename = row[0].rpartition('/')[2]
  fileset.add(filename)
  fileset2.add(filename.rpartition('.')[0][:-1])

subpath = 'm2'
for subdir, dirs, files in os.walk('%s/%s' % (photo_file_path, subpath)):
    for file in files:
        if file not in fileset:
            #check if use downloaded another size
            if file.rpartition('.')[0][:-1] not in fileset2:
                print '%s not in db, searched for %s*' % (file, file.rpartition('.')[0][:-1])
            else:
                print '%s in other size %s, look for %s*' % (file, file.rpartition('.')[0][:-1])
          

#sys.exit(0)
dbcursor = dbconn.cursor()
for row in dbcursor.execute('SELECT url FROM photo_urls'):
  filename = row[0].rpartition('/')[2]
  m = os.path.exists('%s/m/%s' % (photo_file_path, filename)) == True
  a = os.path.exists('%s/a/%s' % (photo_file_path, filename)) == True
  m2 = os.path.exists('%s/m2/%s' % (photo_file_path, filename)) == True

  if a:
      fullpath = '%s/a/%s' % (photo_file_path, filename)
  elif m2:
      fullpath = '%s/m2/%s' % (photo_file_path, filename)
  elif m:
      fullpath = '%s/m/%s' % (photo_file_path, filename)
  else:
      print('File is missing: %s' % filename)
      continue
  size = os.stat(fullpath).st_size
  filetype = mimetypes.guess_type(fullpath)
  if filetype[0] not in ['image/jpeg', 'image/png', 'image/gif']:
      print 'What about filetype %s of %s' % (filetype[0], fullpath)
  if size == 10274:
      print 'File %s has placeholder size of 10274 byte, redownloading %s with all image sizes.' % (filename, row[0])
      for s in ['b', 'c', 'z', '-', 'n', 'm', 'q', 't', 's']:
          u = row[0].replace('b.', '%s.' % s) if row[0].find('b.') <> -1 else row[0].replace('o.', '%s.' % s)
          r = urllib.urlretrieve(u)
          if r[1].dict['content-length'] <> 10274:
              tmpfile = r[0]
              print '  download %s' % u.rpartition('/')[2]
              size2 = os.stat(tmpfile).st_size
              if size2 <> size:
                  print '    OK: downloaded size %s with filesize of %s bytes, replacing' % (s, size2)
                  print '      mv %s %s' % (tmpfile, fullpath)
                  shutil.move(tmpfile, fullpath) 
                  break
dbconn.close()
