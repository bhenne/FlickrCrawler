import os
import sqlite3
import json
import time
import datetime
import pyexiv2
import sys

#imagepath = '/home/henne/crawled_data/Flickr/100k-any/'
#dbfile = '%s/FlickrPhotos-all_in_one.db' % imagepath
#imagepath = '/Users/henne/research_data/LocrFlickr_datasets2/Flickr/Flickr/50k-mobile/'
imagepath = '/Users/henne/research_data/LocrFlickr_datasets2/Flickr/Flickr/100k-any/'
dbfile = '%s/FlickrPhotos.db' % imagepath

dbconn = sqlite3.connect(dbfile)
dbcursor = dbconn.cursor()

debug = False    # or = __debug__

#print 'date\tfilename\toriginal\tphoto_id\tlocation\tlocationexif\tlat_info\tlat_exif'
print 'date\tfilename\toriginal\tphoto_id\tloc_from_file\tloc_exif_flickr\tloc_exif_file\tany_loc\tloc_info_flickr\tmwg_rs\tmp_r'.replace('\t', ';')

errs = 0
errs2 = 0
for root, dirs, files in os.walk(imagepath):
    for name in files:
        o = False
        if name.rpartition('.')[0][-1:] == 'o':
            o = True    #: Flickr original file with embedded metadata
        if name.rpartition('.')[2] in ('jpg', 'jpeg'):
            id = name.partition('_')[0]
            q = 'SELECT json_photo_info, json_photo_exif FROM all_in_one WHERE photo_id=%s' % id
            dbcursor.execute(q)
            r = dbcursor.fetchall()
            if len(r) == 0:
                # do something better here
                errs2 += 1
                sys.stderr.write('#err no db data: %s\n' % id)
                continue

            # READ FLICKR PHOTO INFO
            # get datetime of upload and location
            info = json.loads(r[0][0])
            uploaded =  datetime.datetime.max
            lat_i = ''
            lon_i = ''
            if 'dateuploaded' in info:
                uploaded = int(info['dateuploaded'])
                uploaded2 = datetime.datetime.utcfromtimestamp(uploaded)
                uploaded = time.strftime('%Y:%m:%d %H:%M:%S', time.gmtime(uploaded))
                if debug:
                    print "#  dateuploaded", uploaded, uploaded2
            if 'location' in info:
                lat_i = info['location'][u'latitude']
                lon_i = info['location'][u'longitude']

            # GET FLICKR-STORED EXIF DATA
            # get datetimeOriginal, location and gpsDateTime
            exif = json.loads(r[0][1])
            datetimeoriginal = datetime.datetime.max
            gpsDateTime = datetime.datetime.max
            gpsDate = ''
            gpsTime = ''
            lat_e = ''
            lon_e = ''
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
                    if tag[u'tag'] == u'GPSLongitude':
                        lon_e = tag[u'raw']
                    if tag[u'tag'] == u'GPSDateStamp':
                        gpsDate = tag[u'raw']
                    if tag[u'tag'] == u'GPSTimeStamp':
                        gpsTime = tag[u'raw']
            if gpsDate != '' and gpsTime != '':
                try:
                    gpsDateTime = datetime.datetime.strptime('%s %s' % (gpsDate, gpsTime), '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    gpsDateTime = datetime.datetime.max

            # IF datetimeOriginal was not in FLICKR-EXIF, TRY to read it FROM FILE
            if (datetimeoriginal == datetime.datetime.max) and o == True:
                metadata = pyexiv2.ImageMetadata(os.path.join(root, name))
                try:
                    metadata.read()
                    if 'Exif.Photo.DateTimeOriginal' in metadata.exif_keys:
                        d = metadata['Exif.Photo.DateTimeOriginal'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                    elif 'Exif.Photo.DateTimeDigitized' in metadata.exif_keys:
                        d = metadata['Exif.Photo.DateTimeDigitized'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                    elif 'Exif.Image.DateTime' in metadata.exif_keys:
                        d = metadata['Exif.Image.DateTime'].value
                        #if not d.startswith('   ') == True and not d.startswith('000') == True:
                        if isinstance(d, datetime.datetime):
                            datetimeoriginal = d
                    #else:
                    #    print "# %s" % metadata.exif_keys
                except IOError:
                    pass
            if debug:
                if datetimeoriginal != datetime.datetime.max:
                    print "#  datetimeoriginal", datetimeoriginal

            # IF gpsDateTime was not in FLICKR-EXIF, TRY to read it FROM FILE
            gpsDate = ''
            gpsTime = ''
            if (gpsDateTime == datetime.datetime.max) and o == True:
                try:
                    metadata.read()
                    if 'Exif.GPSInfo.GPSDateStamp' in metadata.exif_keys:
                        gpsDate = metadata['Exif.GPSInfo.GPSDateStamp'].value
                    if 'Exif.GPSInfo.GPSTimeStamp' in metadata.exif_keys:
                        gpsTime = metadata['Exif.GPSInfo.GPSTimeStamp'].value
                except IOError:
                    pass
                if gpsDate != '' and gpsTime != '':
                    try:
                        gpsDateTime = datetime.datetime.strptime('%s %s' % (gpsDate, gpsTime), '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        gpsDateTime = datetime.datetime.max

            if debug:
                if gpsDateTime != datetime.datetime.max:
                    print "#  gpsDateTime", gpsDateTime

            lat_f = ''
            lon_f = ''
            mwg = ''
            mp = ''
            #if (lat_e == None) and o == True:
            if o == True:
                metadata = pyexiv2.ImageMetadata(os.path.join(root, name))
                try:
                    metadata.read()
                    if 'Exif.GPSInfo.GPSLatitude' in metadata.exif_keys and 'Exif.GPSInfo.GPSLongitude' in metadata.exif_keys:
                        lat_f = metadata['Exif.GPSInfo.GPSLatitude'].value
                        lon_f = metadata['Exif.GPSInfo.GPSLongitude'].value
                    elif 'Xmp.exif.GPSLatitude' in metadata.xmp_keys and 'Xmp.exif.GPSLongitude' in metadata.xmp_keys:
                        lat_f = metadata['Xmp.exif.GPSLatitude'].value
                        lon_f = metadata['Xmp.exif.GPSLongitude'].value
                    if 'Xmp.mwg-rs.Regions/mwg-rs:RegionList' in metadata.xmp_keys:
                        if 'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Area/stArea:x' in metadata.xmp_keys and 'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Area/stArea:y' in metadata.xmp_keys:
                            if 'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name' in metadata.xmp_keys and metadata['Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name'].value.strip() != '':
                                mwg = 'named'
                            else:
                                mwg = 'unnamed'
                        elif 'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name' in metadata.xmp_keys and metadata['Xmp.mwg-rs.Regions/mwg-rs:RegionL    ist[1]/mwg-rs:Name'].value.strip() != '':
                            mwg = 'name-only'
                    if 'Xmp.MP.RegionInfo/MPRI:Regions' in metadata.xmp_keys:
                        if 'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:Rectangle' in metadata.xmp_keys:
                            if 'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:PersonDisplayName' in metadata.xmp_keys:
                                mp = 'named'
                            else:
                                mp = 'unnamed'
                        elif 'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:PersonDisplayName' in metadata.xmp_keys:
                            mp = 'name-only'
                except IOError:
                    pass
            # Ref is not used! coordinates are not real ... have no sign
            if type(lat_f) == pyexiv2.utils.NotifyingList:
                lat_f = round(float(lat_f[0]) + float(lat_f[1])/60 + float(lat_f[0])/3600, 5)
            if type(lon_f) == pyexiv2.utils.NotifyingList:
                lon_f = round(float(lon_f[0]) + float(lon_f[1])/60 + float(lon_f[0])/3600, 5)

            l_i = ''
            l_e = ''
            l_f = ''
            if len(unicode(lat_i))+len(unicode(lon_i)) > 0:
                l_i = '%s, %s' % (unicode(lat_i).strip(), unicode(lon_i).strip())
            if len(unicode(lat_e))+len(unicode(lon_e)) > 0:
                l_e = '%s, %s' % (unicode(lat_e).strip(), unicode(lon_e).strip())
            if len(unicode(lat_f))+len(unicode(lon_f)) > 0:
                l_f = '%s, %s' % (unicode(lat_f).strip(), unicode(lon_f).strip())
            if l_e == '0 deg 0\' 0.00", 0 deg 0\' 0.00"':
                l_e = ''
            loc = (lat_e != '' and lon_e !=  '') or (lat_f != '' and lon_f != '')
            loc2 = (lat_i != '' and lon_i != '') or (lat_e != '' and lon_e !=  '') or (lat_f != '' and lon_f != '')
            # USE GPS TIME IF AVAILABLE (note: this is not local time, but UTC), 
            # OTHERWISE EARLIER ONE OF UPLOAD TIME OR datetimeoriginal FROM FILE
            if gpsDateTime != datetime.datetime.max:
                earlier = gpsDateTime
            else:
                earlier = uploaded2 if uploaded2 < datetimeoriginal else datetimeoriginal
            #print id, uploaded, datetimeoriginal, lat_i, lat_e, "     ", earlier, loc
            #print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (earlier, name, o, id, loc, loc2, lat_e != None, lat_i, lat_e)
            print ('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (earlier, name, o, id, loc, l_e, l_f, loc2, l_i, mwg, mp)).replace('\t', ';')
        else:
            errs += 1
            sys.stderr.write('#error: %s\n' % name)

sys.stderr.write('#errors: %s\n' % errs)
sys.stderr.write('#errors db: %s\n' % errs2)

dbcursor.close()
dbconn.close()


##### R #####
# d <- read.csv('loc2.txt', header=TRUE, sep=";", colClasses=c("character", "character", "character", "character", "character", "character", "character", "character", "character"), quote = "")
# d$d <- substr(d$date, 1, 4)
# table(d$d)
# nrow(d[d$d=="2010",])
# nrow(d[d$d=="2010" & d$loc_from_file=="True",])
# 100 / nrow(d[d$d=="2010",]) * nrow(d[d$d=="2010" & d$loc_from_file=="True",])
