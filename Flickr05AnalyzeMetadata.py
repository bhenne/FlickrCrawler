"l""This script reads metadata from image file and Flickr API output, combines it for analysis."""

basepath = 'flickr_photos_test/'
CSVfile = 'flickr_data/FlickrDatasetTest.txt'

import pyexiv2
import codecs
from Flickr03GetNPhotoURLExif import exifjsontodict
import sys, os


PrivateData = {
    'CameraOwner' : [ 'Exif.Canon.OwnerName' ],
    'CameraMaker' : [ 'Exif.Image.Make' ],
    'CameraModel' : [ 'Exif.Image.Model' ],
    'CameraID' : [ 'Exif.Canon.SerialNumber', 'Exif.Fujifilm.SerialNumber', 'Exif.Nikon3.SerialNumber', 'Exif.Pentax.SerialNumber', 'Exif.Photo.0xa431' 
                   'Exif.Nikon3.SerialNO', 'Exif.Olympus.SerialNumber2', 'Exif.Panasonic.InternalSerialNumber', 'Exif.Sigma.SerialNumber', 'Xmp.aux.SerialNumber' ],
    'Artist' : [ 'Exif.Image.Artist', 'Iptc.Application2.Byline', 'Xmp.dc.creator' ],
    'Keywords' : [ 'Iptc.Application2.Keywords', 'Xmp.dc.subject', 'Xmp.lr.hierarchicalSubject'],
    'Description' : [ 'Xmp.dc.description', 'Iptc.Application2.Caption' ],
    #'Description' : [ 'Exif.Image.ImageDescription', 'Xmp.dc.description', 'Iptc.Application2.Caption' ], #ImageDescription contains lots of Camera Model names?!
    'Headline' : [ 'Xmp.photoshop.Headline', 'Iptc.Application2.Headline' ],
    'Location' : [ 'Xmp.iptc.Location', 'Iptc.Application2.SubLocation' ],
    'City' : [ 'Iptc.Application2.City', 'Xmp.photoshop.City' ],
    'State' : [ 'Iptc.Application2.ProvinceState', 'Xmp.photoshop.State' ],
    'Country' : [ 'Iptc.Application2.CountryName', 'Iptc.Application2.CountryCode', 'Xmp.photoshop.Country', 'Xmp.iptc.CountryCode' ],
    'GPSLatitude' : [ 'Exif.GPSInfo.GPSLatitude', 'Xmp.exif.GPSLatitude' ],
    'GPSLongitude' : [ 'Exif.GPSInfo.GPSLongitude', 'Xmp.exif.GPSDestLongitude' ],
    'PersonRegion' : [ 'Xmp.MP.RegionInfo', 'Xmp.MP.RegionInfo/MPRI:Regions', 
                       'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:Rectangle',
                       'Xmp.MP.RegionInfo/MPRI:Regions[1]/MPReg:PersonDisplayName'  ]
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
        return False
    metadata_keys = metadata.keys()
    
    extractedData = {}
    for key in sorted(PrivateData):
        val = set()
        privateFields = PrivateData[key]
        for field in privateFields:
            if field in metadata_keys:
                v = unpack(metadata[field].raw_value)   ### FIX BAD UTF ERRORS
                #v = unpack(metadata[field].value)  ### ALSO HERE BAD UNICODE #!?#!%& and NotifyingList foo
                if v != '':
                    val.add(v)
        if len(val) > 0:
            extractedData[key] = val
    return extractedData

flickr_keys = [ 'flickr_url', 'flickr_tags', 'flickr_title', 'flickr_description', 'flickr_GPS', 'flickr_haspeople',
                'axif_Artist', 'axif_Make', 'axif_Model', 'axif_GPS_lat', 'axif_GPS_lon', 'axif_Title', 'axif_Headline',
                'axif_Description', 'axif_Location', 'axif_City', 'axif_State', 'axif_Country', 'axif_Keywords']

def analyze_apiinfo(path, file):
    if not path.endswith('/'):
        path += '/'
    f = codecs.open('%s%s' % (path, file), 'rt', 'utf-8')
    url, exifjson, tags, subtitles, location, people = f.readlines()
    f.close()
    exif = exifjsontodict(exifjson)
    
    extractedData = {}
    extractedData['flickr_url'] = url.strip('\n')
    extractedData['flickr_tags'] = u','.join(eval(tags.strip('\n')))
    subtitles = eval(subtitles)
    extractedData['flickr_title'] = unicode(subtitles[0])
    extractedData['flickr_description'] = unicode(subtitles[1])
    location = eval(location)
    if len(location) <> 2 or ((len(location) == 2) and (location[0]+location[1] == 0)):
        extractedData['flickr_GPS'] = ''
    else:
        extractedData['flickr_GPS'] = u','.join([str(l) for l in location])
    extractedData['flickr_haspeople'] = people.strip('\n')
    
    if 'Artist' in exif and len(exif['Artist'].strip()) > 0:
        extractedData['axif_Artist'] = exif['Artist']
    if 'Creator' in exif and len(exif['Creator'].strip()) > 0:
        extractedData['axif_Artist'] = exif['Creator']
    if 'Model' in exif and len(exif['Model'].strip()) > 0:
        extractedData['axif_Model'] = exif['Model']
    if 'Make' in exif and len(exif['Make'].strip()) > 0:
        extractedData['axif_Make'] = exif['Make']
    if 'GPS_lat' in exif and len(exif['GPS_lat'].strip()) > 0:
        extractedData['axif_GPS_lat'] = exif['GPS_lat']
    if 'GPS_lon' in exif and len(exif['GPS_lon'].strip()) > 0:
        extractedData['axif_GPS_lon'] = exif['GPS_lon']
    if 'Title' in exif and len(exif['Title'].strip()) > 0:
        extractedData['axif_Title'] = exif['Title']
    if 'Headline' in exif and len(exif['Headline'].strip()) > 0:
        extractedData['axif_Headline'] = exif['Headline']
    if 'Description' in exif and len(exif['Description'].strip()) > 0:
        extractedData['axif_Description'] = exif['Description']
    if 'Location' in exif and len(exif['Location'].strip()) > 0:
        extractedData['axif_Location'] = exif['Location']
    if 'City' in exif and len(exif['City'].strip()) > 0:
        extractedData['axif_City'] = exif['City']
    if 'State' in exif and len(exif['State'].strip()) > 0:
        extractedData['axif_State'] = exif['State']
    if 'Country' in exif and len(exif['Country'].strip()) > 0:
        extractedData['axif_Country'] = exif['Country']
    if 'Keywords' in exif and len(exif['Keywords'].strip()) > 0:
        extractedData['axif_Keywords'] = exif['Keywords'].replace(';',',')
    if 'Subject' in exif and len(exif['Subject'].strip()) > 0:
        extractedData['axif_Keywords'] = exif['Subject'].replace(';',',')

    return extractedData


def work_on_file(basepath, filename):
    if not basepath.endswith('/'):
        basepath += '/'
    photo_path = basepath+'photos/'
    apiinfo_path = basepath+'infos/'
    data = {}
    p = analyze_photo(photo_path, filename)
    x = analyze_apiinfo(apiinfo_path, filename+'.txt')
    if (p == False) or (x == False):
        return ''
    data.update(analyze_photo(photo_path, filename))
    data.update(analyze_apiinfo(apiinfo_path, filename+'.txt'))

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
    path = basepath+'photos/'
    listing = os.listdir(path)
    out.write(headline())
    out.write('\n')
    l = 0
    for file in listing:
        if (file.endswith('.jpg') or file.endswith('.jpeg')) and (os.path.isfile('%sinfos/%s.txt' % (basepath, file)) == True):
            line = work_on_file(basepath, file)
            if line == '':
                continue
            out.write(line.replace('\n', ' '))
            out.write('\n')
            l += 1
            sys.stdout.write('%s\n' % l)
        else:
            sys.stderr.write('No suitable file: %s\n' % file)
    return l


f = codecs.open(CSVfile, 'wt', 'utf-8')
count = iterate_files(basepath, f)
f.close()
print 'Written %d lines.' % count
