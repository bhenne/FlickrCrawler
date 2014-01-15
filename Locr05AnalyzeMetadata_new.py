#!/bin/env python # -*- coding: utf-8 -*-

"""This script reads metadata from image file and Flickr API output from sqlite DB, combines it for analysis."""

basepath = '/Users/henne/research_data/LocrFlickr_datasets1/locr-files/jpg+html'
#basepath = '/Users/henne/research_data/LocrFlickr_datasets2/locr-files/jpg+html'
CSVfile = 'LocrDataset-5k-new.txt'
#CSVfile = 'LocrDataset-25k-new.txt'

import sys
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

def _try2utf8_encode(unicode_data):
    chars = []
    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            chars.append(char.encode('utf-8', 'strict'))
        except UnicodeError:
            #chars.append(unichr(ord(char)))
            pass
    return ''.join(chars)

def removeControlCharacters(line):
    newln = ''
    for c in line:
        if c >= chr(32):
            newln = newln + c
    return newln

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

def analyze_html(path, file):
    extractedData = {}
    if not path.endswith('/'):
        path += '/'
    #f = codecs.open('%s%s' % (path, file), 'r', 'utf-8', 'strict')
    f = codecs.open('%s%s' % (path, file), 'r', 'utf-8', 'replace')
    try:
      s = f.read()
    except UnicodeDecodeError:
      f = codecs.open('%s%s' % (path, file), 'r', 'latin-1', 'strict')
      s = f.read()
    from lxml import etree
    r = etree.HTML(s)

    loc = r.xpath('.//meta[@name="icbm"]')
    if len(loc) > 0:
        loc_value = loc[0].get('content')
    else:
        print 'PLEASE CALL LocrCleanup! there are wrong files, maybe proxy/download errors at crawling'
        sys.exit(-1)
    if loc_value != '0, 0':
        extractedData['HTML.LatLong'] = loc_value

    ref = r.xpath('.//h5[@class="BROWSE_CONTENT_SORT_TITLE"]')
    if len(ref) > 0:
        childs = ref[0].getnext().getnext().getchildren()
        for i in xrange(0,len(childs),3):
            tag = childs[i].text
            val = _try2utf8_encode(childs[i+1].getchildren()[0].text)
            if tag == u'Kontinent:':
                extractedData['HTML.Continent'] = val
            elif tag == u'Land:':
                extractedData['HTML.Country'] = val
            elif tag == u'Bundesland:':
                extractedData['HTML.State'] = val
            elif tag == u'Stadt:':
                extractedData['HTML.City'] = val
            elif tag == u'Postleitzahl:':
                extractedData['HTML.Postcode'] = val
            elif tag == u'Straße:':
                extractedData['HTML.Street'] = val
            #print tag, unpack(val)

    taglist = []
    tags = r.xpath('.//div[@id="LOCR_PHOTOS_TAGS"]')
    if len(tags) > 0:
        lis = tags[0].xpath('.//li')
        if len(lis) > 0:
            for li in lis:
                taglist.append(li.getchildren()[0].text)
        extractedData['HTML.Tags'] = u', '.join(taglist)

    return extractedData


HTML_keys = [ 'HTML.Tags', 'HTML.LatLong', 'HTML.Continent', 'HTML.Country', 'HTML.State', 'HTML.City', 'HTML.Postcode', 'HTML.Street' ]

def headline():
    headline = u'#'
    for fieldname in sorted(PrivateData):
        headline += fieldname
        headline += ';'
    for fieldname in sorted(HTML_keys):
        headline += fieldname
        headline += ';'
    headline += 'locr_rel_url'
    return headline

def work_on_file(basepath, filename):
    if not basepath.endswith('/'):
        basepath += '/'
    path = photo_path = basepath
    data = {}
    p = analyze_photo(photo_path, filename)
    x = analyze_html(path, filename+'.html')
    if (p == False) or (x == False):
        return ''
    data.update(analyze_photo(photo_path, filename))
    data.update(analyze_html(path, filename+'.html'))

    line = u''
    for privateField in sorted(PrivateData):
        if privateField in data:
            line += unpack(data[privateField]).replace(';', ',')
            if line.endswith('\\') == True:
                line = line.rpartition('\\')[0]
        line += ';'
    
    for privateField in sorted(HTML_keys):
        if privateField in data:
            tmp = unpack(data[privateField])
            tmp = tmp.replace(';', ',')
            print type(tmp), tmp
            tmp = _try2utf8_encode(tmp)
            print type(tmp), tmp
            #tmp = tmp.encode('raw_unicode_escape')
            #tmp = tmp.encode('unicode_escape')
            print type(tmp), tmp
            try:
              line += tmp
            except:
              print type(line), type(tmp), line, tmp
              line += tmp
            if line.endswith('\\') == True:
                line = line.rpartition('\\')[0]
        line += ';'
    line += _try2utf8_encode(filename)
#    line += ';'
#    line += filename.rpartition('.')[0][len(filename.rpartition('.')[0])-1]
    return line


def headline():
    headline = u'#'
    for fieldname in sorted(PrivateData):
        headline += fieldname
        headline += ';'
    for fieldname in sorted(HTML_keys):
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
        if (file.startswith('photo-') and not file.endswith('.html')):
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

f = codecs.open(CSVfile, 'wt', 'utf-8')
count = iterate_files(basepath, f)
f.close()
print 'Written %d lines.' % count
