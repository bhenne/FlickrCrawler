import os
import sqlite3
import json
import time
import datetime
import pyexiv2
import math
import sys

#imagepath = '/home/henne/crawled_data/Flickr/100k-any/'
#dbfile = '%s/FlickrPhotos-all_in_one.db' % imagepath
imagepath = '/Users/henne/research_data/LocrFlickr_datasets2/Flickr/Flickr/50k-mobile/'
dbfile = '%s/FlickrPhotos.db' % imagepath

dbconn = sqlite3.connect(dbfile)
dbcursor = dbconn.cursor()

c = 0
for root, dirs, files in os.walk(imagepath):
    for name in files:
        if c % 500 == 0:
            sys.stderr.write('%s\n' % c)
        c += 1
        o = False
        if name.rpartition('.')[0][-1:] == 'o':
            o = True
        if name.rpartition('.')[2] in ('jpg', 'jpeg'):
            id = name.partition('_')[0]
            q = 'SELECT json_photo_info, json_photo_exif FROM all_in_one WHERE photo_id=%s' % id
            dbcursor.execute(q)
            r = dbcursor.fetchall()
            if len(r) == 0:
                # do something better here
                continue
            info = json.loads(r[0][0])
            uploaded =  datetime.datetime.max
            lat_i = None
            if 'dateuploaded' in info:
                uploaded = int(info['dateuploaded'])
                uploaded2 = datetime.datetime.utcfromtimestamp(uploaded)
                uploaded = time.strftime('%Y:%m:%d %H:%M:%S', time.gmtime(uploaded))
            exif = json.loads(r[0][1])
            datetimeoriginal = datetime.datetime.max
            lat_e = None
            for tag in exif:
                if u'tag' in tag:
                    if tag[u'tag'] == u'DateTimeOriginal':
                        datetimeoriginal = tag[u'raw']
                        if datetimeoriginal.startswith('   ') == True or datetimeoriginal.startswith('000') == True:
                            datetimeoriginal = datetime.datetime.max
                        else:
                            try:
                                datetimeoriginal = datetime.datetime.strptime(datetimeoriginal, '%Y:%m:%d %H:%M:%S')
                            except ValueError:
                                datetimeoriginal = datetime.datetime.max
                    if tag[u'tag'] == u'GPSLatitude':
                        lat_e = tag[u'raw']
            d0 = datetimeoriginal
            d1 = d2 = d3 = ''
            if (datetimeoriginal == datetime.datetime.max) and o == True:
                metadata = pyexiv2.ImageMetadata(os.path.join(root, name))
                try:
                    metadata.read()
                    if 'Exif.Photo.DateTimeOriginal' in metadata.exif_keys:
                        d = metadata['Exif.Photo.DateTimeOriginal'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                            d1 = d
                    if 'Exif.Photo.DateTimeDigitized' in metadata.exif_keys:
                        d = metadata['Exif.Photo.DateTimeDigitized'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                            d2 = d
                    if 'Exif.Image.DateTime' in metadata.exif_keys:
                        d = metadata['Exif.Image.DateTime'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                            d3 = d
                    #else:
                    #    print metadata.exif_keys
                except IOError:
                    pass
            dd0 = dd1 = dd2 = dd3 = ''
            dd0 = dd1 = dd2 = dd3 = 999999
            if d0 != datetime.datetime.max:
                dd0 = math.fabs((d0 - uploaded2).total_seconds() * 1.0 / 60)
            if d1 != '':
                dd1 = math.fabs((d1 - uploaded2).total_seconds() * 1.0 / 60)
            if d2 != '':
                dd2 = math.fabs((d2 - uploaded2).total_seconds() * 1.0 / 60)
            if d3 != '':
                dd3 = math.fabs((d3 - uploaded2).total_seconds() * 1.0 / 60)
            if len('%s%s%s' % (d1, d2, d3)) > 0 or d0 != datetime.datetime.max:
                #print ' / '.join([str(x) for x in [uploaded2, datetimeoriginal, d1, d2, d3, dd0, dd1, dd2, dd3]])
                print min(dd0, dd1, dd2, dd3)
#            if (lat_e == None) and o == True:
#                metadata = pyexiv2.ImageMetadata(os.path.join(root, name))
#                try:
#                    metadata.read()
#                    if 'Exif.GPSInfo.GPSLatitude' in metadata.exif_keys:
#                        lat_e = metadata['Exif.GPSInfo.GPSLatitude']
#                    elif 'Xmp.exif.GPSLatitude' in metadata.xmp_keys:
#                        lat_e = metadata['Xmp.exif.GPSLatitude']
#                except IOError:
#                    pass
#            loc = lat_i != None or lat_e != None
#            earlier = uploaded2 if uploaded2 < datetimeoriginal else datetimeoriginal
#            #print id, uploaded, datetimeoriginal, lat_i, lat_e, "     ", earlier, loc
#            print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (earlier, name, o, id, loc, lat_e != None, lat_i, lat_e)
#        #else:
#        #    print 'error: %s' % name


dbcursor.close()
dbconn.close()
