"""This script reads metadata from image file and Flickr API output from sqlite DB, combines it for analysis."""

basepath = '/mnt/WORKING-ON/100k-any'
basepath = '/mnt/WORKING-ON/50k-mobile'
dbfile = 'FlickrPhotos-all_in_one.db'
CSVfile = 'FlickrDataset-100k-new.txt'
CSVfile = 'FlickrDataset-50k-new.txt'

import sys
sys.path.insert(0,"python-flickr-api")
import pyexiv2
import sqlite3
import json
import codecs
#from Flickr03GetNPhotoURLExif import exifjsontodict
import os
import re
import datetime

dbcursor = None

pyexiv2.xmp.register_namespace('http://ns.adobe.com/lightroom/1.0/', 'lr')
pyexiv2.xmp.register_namespace('http://ns.apple.com/faceinfo/1.0/', 'apple-fi')


PrivateData = {
    'CameraOwner' : [ 'Exif.Photo.CameraOwnerName', 'Exif.Canon.OwnerName', ],
    'CameraID' : [ 'Exif.Canon.InternalSerialNumber', 'Exif.Canon.SerialNumber',
                   'Exif.Fujifilm.SerialNumber', 'Exif.Image.CameraSerialNumber',
                   'Exif.Nikon3.SerialNO', 'Exif.Nikon3.SerialNumber',
                   'Exif.Olympus.SerialNumber2', 'Exif.OlympusEq.InternalSerialNumber',
                   'Exif.OlympusEq.SerialNumber', 'Exif.Panasonic.InternalSerialNumber',
                   'Exif.Pentax.SerialNumber', 'Exif.Photo.BodySerialNumber',
                   'Exif.Sigma.SerialNumber', 'Xmp.aux.SerialNumber',
                   'Xmp.MicrosoftPhoto.CameraSerialNumber', ],
    'Artist' : [ 'Exif.Image.Artist', 'Xmp.tiff.Artist', 'Xmp.xmpDM.artist',
                 'Iptc.Application2.Byline', 'Xmp.dc.creator', 'Xmp.iptcExt.AOCreator',
                 'Xmp.plus.ImageCreatorName', ],
    'Copyright' : [ 'Exif.Image.Copyright', 'Xmp.plus.CopyrightOwnerName', ],
    'Keywords' : [ 'Exif.Image.XPKeywords', 'Iptc.Application2.Keywords',
                   'Xmp.dc.Subject', 'Exif.Image.XPKeywords',
                   'Xmp.lr.hierarchicalSubject', ],
    'Headline' : [ 'Iptc.Application2.Headline', 'Exif.Image.ImageDescription',
                   'Exif.Image.XPTitle', 'Xmp.dc.title', 'Xmp.photoshop.Headline', ],
    'Description' : [ 'Iptc.Application2.Caption', 'Exif.Photo.UserComment', 'Exif.Image.UserComment',
                      'Xmp.dc.description', 'Xmp.tiff.ImageDescription', ], # caption=abstract in Iptc case...
                    # Attention !!! 'Description' : [  #ImageDescription contains lots of Camera Model names?!
    'CameraMaker' : [ 'Exif.Image.Make' ],
    'CameraModel' : [ 'Exif.Image.Model' ],
    'GPSLatitude' : [ 'Exif.GPSInfo.GPSLatitude', 'Xmp.exif.GPSLatitude',
                      'Exif.GPSInfo.GPSDestLatitude', 'Xmp.exif.GPSDestLatitude' ],
    'GPSLongitude' : [ 'Exif.GPSInfo.GPSLongitude', 'Xmp.exif.GPSLongitude',
                       'Exif.GPSInfo.GPSDestLongitude', 'Xmp.exif.GPSDestLongitude', ],
    'UnkownLocation' : [ 'Exif.Samsung2.LocationName', 'Exif.Samsung2.LocalLocationName', # http://www.flickr.com/photos/frankeggen/9336533018/meta/
                         'Exif.Pentax.Location', ],
    'Country' : [ 'Iptc.Application2.CountryCode', 'Iptc.Application2.CountryName',
                  'Iptc.Application2.LocationCode', 'Xmp.photoshop.Country',
                  'Xmp.iptcExt.CountryCode', 'Xmp.iptcExt.CountryName',
                  'Xmp.iptc.CountryCode', ],
    'State' : [ 'Iptc.Application2.ProvinceState', 'Xmp.iptcExt.ProvinceState',
                'Xmp.photoshop.State', ],
    'City': [ 'Iptc.Application2.City', 'Xmp.iptcExt.City',
              'Xmp.photoshop.City', ],
    'Location' : [ 'Iptc.Application2.SubLocation', 'Iptc.Application2.LocationName', # could also be country ... "according to guidelines of the provider."
                   'Xmp.iptc.Location', 'Xmp.iptcExt.SubLocation',
                   'Xmp.iptcExt.LocationShown', 'Xmp.iptcExt.LocationCreated',
                   'Xmp.xmpDM.shotLocation', ],
    'PersonRegion' : [ 'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:Rectangle',
                       'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Area', ],
    'PersonRegionName' : [ 'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:PersonDisplayName',
                         'Xmp.mwg-rs.Regions/mwg-rs:RegionList[1]/mwg-rs:Name', ],
}


def unpack(x):
    if type(x) == str:
        return x.strip()#decode("utf-8", "replace").strip()
    elif type(x) == list:
          return u', '.join(['%r'%e for e in x])#.decode("utf-8", "replace")
    elif type(x) == dict:
        l = []
        for k, v in x.iteritems():
            l.append(u'%s:%r' % (k, v))
        return unpack(l)
    elif isinstance(x, set):
        l = []
        for i in x:
            l.append(i)
        return unpack(l)
    else:
        return x

def analyze_photo(path, file):
    if not path.endswith('/'):
        path += '/'
    metadata = pyexiv2.ImageMetadata('%s%s' % (path, file))
    try:
        metadata.read()
    except IOError, strerror:
        print "I/O error on file %s: %s" % (file, strerror)
        #return False
        return {}
    metadata_keys = metadata.keys()
    
    extractedData = {}
    for key in sorted(PrivateData):
        val = set()
        privateFields = PrivateData[key]
        for field in privateFields:
            if field in metadata_keys:
                v = unpack(metadata[field].raw_value)   ### FIX BAD UTF ERRORS
                #v = unpack(metadata[field].value)  ### ALSO HERE BAD UNICODE #!?#!%& and NotifyingList foo
                # cleanup values
                i = 0
                while i < 10:
                    if re.match('^[\d-]+$', v) is not None:
                        break
                    if v.upper() == v and (re.match('^[\w\s-]+$', v) is not None and re.match('^[\D-]+$', v) is not None):
                        v = ''
                        break
                    if v == 'unknown':
                        v = ''
                        break
                    v.replace('\x00','')
                    if v.startswith("u'") or v.startswith('u"'):
                        v = v.lstrip('u')
                    if v.startswith('charset="Ascii"'):
                        v = v.lstrip('charset="Ascii"')
                    if v.startswith('charset="InvalidCharsetId"'):
                        v = v.lstrip('charset="InvalidCharsetId"')
                    if v.startswith('x-default:'):
                        v = v.lstrip('x-default:')
                    v = v.strip("\"'")
                    v = v.strip('\x00')
                    v = v.strip(' ')
                    i += 1
                if v != '':
                    val.add(v)
        if len(val) > 0:
            extractedData[key] = val
    return extractedData

flickr_keys = [ 'flickr_url', 'flickr_tags', 'flickr_title', 'flickr_description', 'flickr_GPS', 'flickr_haspeople', 
                'axif_Artist', 'axif_CameraID', 'axif_CameraMaker', 'axif_CameraModel', 'axif_CameraOwner', 
                'axif_City', 'axif_Copyright', 'axif_Country', 'axif_Description', 'axif_GPSLatitude', 
                'axif_GPSLongitude', 'axif_Headline', 'axif_Keywords', 'axif_Location', 'axif_PersonRegion', 
                'axif_PersonRegionName', 'axif_State', 'axif_UnkownLocation' ]

flickrexiflist = [
    ('IFD0', 'ImageDescription', 'Description'),
    ('IFD0', 'Make', 'CameraMaker'),
    ('IFD0', 'Model', 'CameraModel'),
    ('IFD0', 'Artist', 'Artist'),
    ('IFD0', 'Copyright', 'Copyright'),
    ('IFD0', 'XPTitle', 'Headline'),
    ('IFD0', 'XPKeywords', 'Keywords'),
    ('IFD0', 'CameraSerialNumber', 'CameraID'),
    ('ExifIFD', 'UserComment', 'Description'),
    ('ExifIFD', 'OwnerName', 'CameraOwner'),
    ('ExifIFD', 'DateTimeOriginal', 'Date_original'),
    ('ExifIFD', 'CreateDate', 'Date_digitized'),
    ('GPS', 'GPSTimeStamp', 'GPS_time'),
    ('GPS', 'GPSDateStamp', 'GPS_date'),
    ('GPS', 'GPSLatitude', 'GPSLatitude'),
    ('GPS', 'GPSDestLatitude', 'GPSLatitude'),
    ('GPS', 'GPSLongitude', 'GPSLongitude'),
    ('GPS', 'GPSDestLongitude', 'GPSLongitude'),
    ('XMP-microsoft', 'CameraSerialNumber', 'CameraID'),
    ('XMP-dc', 'Subject', 'Keywords'),
    ('XMP-dc', 'Creator', 'Artist'),
    ('XMP-dc', 'Title', 'Headline'),
    ('XMP-dc', 'Description', 'Description'),
    ('XMP-photoshop', 'Headline', 'Headline'),
    ('XMP-photoshop', 'Country', 'Country'),
    ('XMP-photoshop', 'State', 'State'),
    ('XMP-photoshop', 'City', 'City'),
    ('XMP-plus', 'CopyrightOwnerName', 'Copyright'),
    ('XMP-plus', 'ImageCreatorName', 'Artist'),
    ('XMP-tiff', 'Artist', 'Artist'),
    ('XMP-tiff', 'ImageDescription', 'Description'),
    ('XMP-xmpDM', 'Artist', 'Artist'),
    ('XMP-xmpDM', 'ShotLocation', 'Location'),
    ('XMP-iptcExt', 'CountryCode', 'Country'),
    ('XMP-iptcExt', 'CountryName', 'Country'),
    ('XMP-iptcExt', 'ProvinceState', 'State'),
    ('XMP-iptcExt', 'City', 'City'),
    ('XMP-iptcExt', 'SubLocation', 'Location'),
    ('XMP-iptcExt', 'AOCreator', 'Artist'),
    ('XMP-iptcExt', 'LocationShown', 'Location'),
    ('XMP-iptcExt', 'LocationCreated', 'Location'),
    ('XMP-iptcCore', 'CountryCode', 'Country'),
    ('XMP-iptcCore', 'Location', 'Location'),
    ('XMP-MP', 'RegionPersonDisplayName', 'PersonRegionName'),
    ('XMP-MP', 'RegionRectangle', 'PersonRegion'),
    ('XMP-lr', 'HierarchicalSubject', 'Keywords'),
    ('XMP-mwg-rs', 'RegionName', 'PersonRegionName'),
    ('Canon', 'CameraOwner', 'CameraOwner'),
    ('Canon', 'SerialNumber', 'CameraID'),
    ('Kodak', 'SerialNumber', 'CameraID'),
    ('MetaIFD', 'SerialNumber', 'CameraID'),
    ('Nikon', 'SerialNumber', 'CameraID'),
    ('Olympus', 'SerialNumber', 'CameraID'),
    ('Pentax', 'SerialNumber', 'CameraID'),
    ('Ricoh', 'SerialNumber', 'CameraID'),
    ('Sigma', 'SerialNumber', 'CameraID'),
    ('XMP-aux', 'OwnerName', 'CameraOwner'),
    ('XMP-aux', 'SerialNumber', 'CameraID'),
    ('IPTC', 'By-line', 'Artist'),
    ('IPTC', 'Keywords', 'Keywords'),
    ('IPTC', 'Headline', 'Headline'),
    ('IPTC', 'Caption-Abstract', 'Description'),
    ('IPTC', 'Country-PrimaryLocationCode', 'Country'),
    ('IPTC', 'Country-PrimaryLocationName', 'Country'),
    ('IPTC', 'ContentLocationCode', 'Country'),
    ('IPTC', 'Province-State', 'State'),
    ('IPTC', 'City', 'City'),
    ('IPTC', 'Sub-location', 'Location'),
    ('IPTC', 'ContentLocationName', 'Location'),
        ]

def exiftodict(exif):
    """Transforms a Flickr Exif object to a dict"""
    if len(exif) == 0:
        return {}
    if type(exif[0]) is not dict:
        e = [x.__dict__ for x in exif]
    else:
        e = exif
    tags = {}
    for tag in e:
        for i in flickrexiflist:
            # flickrexiflist = [ (tagspace, tag, mapping) ]
            if tag['tagspace'] == i[0] and tag['tag'] == i[1] and tag['raw'] is not None:
                tags[i[2]] = tags.get(i[2], u',') + tag['raw']
    for k in tags.keys():
        tags[k] = tags[k].lstrip(',')
    return tags


def analyze_apiinfo(file):
    dbcursor.execute('SELECT json_photo_exif, json_photo_info, url FROM all_in_one WHERE url LIKE "%%%s"' % file)
    r = dbcursor.fetchall()
    if len(r) != 1:
        #return False
        return {}

    exifjson, flickrinfo, url = r[0]
    flickrinfo = json.loads(flickrinfo)
    people = flickrinfo['people']['haspeople']
    location = ''
    if 'location' in flickrinfo:
        loc = flickrinfo['location']
        if 'latitude' in loc and 'longitude' in loc:
            location = '%s,%s' % (loc['latitude'], loc['longitude'])
    tags = []
    if 'tags' in flickrinfo:
        taglist = flickrinfo['tags']
        for t in taglist:
            tags.append(t['text'])
        tags = ','.join(tags)

    exifjson = exifjson.rstrip('\n').replace('false','False').replace('null','None')
    if exifjson != '':
        exif = exiftodict(eval(exifjson))
    else:
        exif = {}
    
    extractedData = {}
    extractedData['flickr_url'] = url
    extractedData['flickr_tags'] = tags
    extractedData['flickr_title'] = flickrinfo['title'] if 'title' in flickrinfo else ''
    extractedData['flickr_description'] = flickrinfo['description'] if 'description' in flickrinfo else ''
    extractedData['flickr_GPS'] = location
    extractedData['flickr_haspeople'] = str(people)

    try:
        for k in exif.keys():
            extractedData['axif_%s' % k] = exif[k]
    except:
        print exif
        raise

    return extractedData


def work_on_file(basepath, filename):
    if not basepath.endswith('/'):
        basepath += '/'
    photo_path = basepath
    data = {}
    p = analyze_photo(photo_path, filename)
    x = analyze_apiinfo(filename)
    if (p == False) or (x == False):
        return ''
    data.update(analyze_photo(photo_path, filename))
    data.update(analyze_apiinfo(filename))

    line = u''
    for privateField in sorted(PrivateData):
        if privateField in data:
            line += unpack(data[privateField]).replace(';', ',')
            if line.endswith('\\') == True:
                line = line.rpartition('\\')[0]
        line += ';'
    
    for privateField in sorted(flickr_keys):
        if privateField in data:
            line += unpack(data[privateField]).replace(';', ',')
            if line.endswith('\\') == True:
                line = line.rpartition('\\')[0]
        line += ';'
    
    line += filename
    line += ';'
    line += filename.rpartition('.')[0][len(filename.rpartition('.')[0])-1]
    return line


def headline():
    headline = u'#'
    for fieldname in sorted(PrivateData):
        headline += fieldname
        headline += ';'
    for fieldname in sorted(flickr_keys):
        headline += fieldname
        headline += ';'
    headline += 'filename'
    headline += ';filesize'
    return headline

def iterate_files(basepath, out='sys.stdout'):
    if not basepath.endswith('/'):
        basepath += '/'
    listing = os.listdir(basepath)
    out.write(headline())
    out.write('\n')
    l = 0
    before = datetime.datetime.now() - datetime.timedelta(minutes=2)
    for file in listing:
        if (file.endswith('.jpg') or file.endswith('.jpeg')):
            line = work_on_file(basepath, file)
            if line == '':
                continue
            out.write(line.replace('\n', ' '))
            out.write('\n')
            l += 1
            #if l % 100 == 0:
            now = datetime.datetime.now()
            if (now - before) > datetime.timedelta(minutes=1):
                before = now
                sys.stdout.write('%s\n' % l)
        else:
            sys.stderr.write('Ignoring: %s\n' % file)
    return l

dbconn = sqlite3.connect(os.path.join(basepath, dbfile))
dbcursor = dbconn.cursor()

f = codecs.open(CSVfile, 'wt', 'utf-8')
count = iterate_files(basepath, f)
f.close()
print 'Written %d lines.' % count
