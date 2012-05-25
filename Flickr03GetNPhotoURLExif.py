"""This script reads Photos from each crawled users Photos file and retrieves n Photos file URLs, Exif information and tags.
"""


n = 1                       # retrieve n photos
skip = 0                    # skip the first skip photos, maybe at a second run
max_photos= 21000           # stop if max_photos photos retrieved
max_links_per_file = 1000   # maximum of links per download links file

photolists_directory = 'flickr_photos_test/'
photoinfo_directory  = 'flickr_photos_test/infos/'


import flickr_api       #APICALL (once)
import csv
import json
import codecs
import sys, os, time


def iterate_photos_directory(path):
    """Yields photolist file names"""
    if not path.endswith('/'):
        path += '/'
    listing = os.listdir(path)
    for file in listing:
        if os.path.isfile('%s%s' % (path, file)):
            yield '%s%s' % (path, file)

def read_Photos(file):
    photos = []
    c_skip = 0
    c_n = 0
    csvReader = csv.reader(open(file, 'rt'), delimiter=';')
    for row in csvReader:
        if len(row) == 1:
            continue
        if skip > c_skip:
            c_skip += 1
            continue
        p = flickr_api.Photo(owner_nsid=row[0], id=row[1], secret=row[2],
                              farm=int(row[3]), server=int(row[4]), title=row[5])
        photos.append(p)
        c_n += 1
        if c_n >= n:
            break
    return photos

def getPhotoFile(photoinfo, noOriginal='b'):
    if 'originalsecret' in photoinfo and 'originalformat' in photoinfo:
        return 'http://farm%s.static.flickr.com/%s/%s_%s_o.%s' % (photoinfo['farm'], photoinfo['server'], 
                                                                   photoinfo['id'], photoinfo['originalsecret'], 
                                                                   photoinfo['originalformat'])
    else:
        return 'http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg' % (photoinfo['farm'], photoinfo['server'], 
                                                                   photoinfo['id'], photoinfo['secret'], noOriginal)

def getPhotoFilename(photofileURL):
    return photofileURL.rpartition('/')[2]

def exiftojson(exif, sort_keys=True):
    """Tranforms a Flickr Exif object to a JSON string"""
    if exif is None:
        return ''
    e = [x.__dict__ for x in exif]
    return json.dumps(e, sort_keys=sort_keys)

def exifjsontodict(exifjson):
    """Transforms Exif information from Flickr object stored as JSON to a dict"""
    try:
        return exiftodict(json.loads(exifjson))
    except ValueError:
        return {}
    
def exiftodict(exif):
    """Transforms a Flickr Exif object to a dict"""
    if len(exif) == 0:
        return []
    if type(exif[0]) is not dict:
        e = [x.__dict__ for x in exif]
    else:
        e = exif
    tags = {}
    for tag in e:
        if tag['label'] == 'Make':
            tags['Make'] = tag['raw']
        elif tag['label'] == 'Model':
            tags['Model'] = tag['raw']
        elif tag['label'] == 'Date and Time (Digitized)':
            tags['Date_digitized'] = tag['raw']
        elif tag['label'] == 'Date and Time (Original)':
            tags['Date_original'] = tag['raw']
        elif tag['label'] == 'GPS Latitude':
            tags['GPS_lat'] = tag['raw']
        elif tag['label'] == 'GPS Longitude':
            tags['GPS_lon'] = tag['raw']
        elif tag['label'] == 'GPS Time Stamp':
            tags['GPS_time'] = tag['raw']
        elif tag['label'] == 'Image Description':
            tags['Description'] = tag['raw']
        elif tag['label'] == 'Artist':
            tags['Artist'] = tag['raw']
        elif tag['label'] == 'Location':
            tags['Location'] = tag['raw']
        elif tag['label'] == 'Creator':
            tags['Creator'] = tag['raw']
        elif tag['label'] == 'Description':
            tags['Description'] = tag['raw']
        elif tag['label'] == 'Subject':
            tags['Subject'] = tag['raw']
        elif tag['label'] == 'Title':
            tags['Title'] = tag['raw']
        elif tag['label'] == 'Hierarchical Subject':
            tags['Subject'] = tag['raw']
        elif tag['label'] == 'City':
            tags['City'] = tag['raw']
        elif tag['label'] == 'Country':
            tags['Country'] = tag['raw']
        elif tag['label'] == 'Country Code':
            tags['Country'] = tag['raw']
        elif tag['label'] == 'Headline':
            tags['Headline'] = tag['raw']
        elif tag['label'] == 'State':
            tags['State'] = tag['raw']
        elif tag['label'] == 'Keywords':
            tags['Keywords'] = tag['raw']
        elif tag['label'] == 'By-line':
            tags['Artist'] = tag['raw']
        elif tag['label'] == 'Sub-location':
            tags['Location'] = tag['raw']
        elif tag['label'] == 'Province- State':
            tags['State'] = tag['raw']
        elif tag['label'] == 'Country- Primary Location Code':
            tags['Country'] = tag['raw']
        elif tag['label'] == 'Country- Primary Location Name':
            tags['Country'] = tag['raw']
        elif tag['label'] == 'Headline':
            tags['Headline'] = tag['raw']
        elif tag['label'] == 'Caption- Abstract':
            tags['Description'] = tag['raw']
    return tags

def infototags(fileinfo):
    """Extracts tags from Flickr Photo.getInfo()'s result"""
    tags = []
    for tag in fileinfo['tags']:
        tags.append(tag['raw'].replace(';',','))
    return tags

def infotosubtitles(fileinfo):
    """Extracts title/description from Flickr Photo.getInfo()'s result"""
    return [fileinfo['title'], fileinfo['description']]

def infotolocation(fileinfo):
    """Extracts location information from Flickr Photo.getInfo()'s result"""
    if 'location' in fileinfo:
        if 'latitude' in fileinfo['location'] and 'longitude' in fileinfo['location']:
            return [ fileinfo['location']['latitude'] , fileinfo['location']['longitude'] ]
        else:
            return [ 0, 0 ]
    else:
        return []

def infotopeople(fileinfo):
    """Extracts people information (has people?) from Flickr Photo.getInfo()'s result
    
    Return 0 is no people, 1 if people. If needed people count can be gotten via 
    extra API call using Photo.getPeople and its length."""
    if 'people' in fileinfo:
        if 'haspeople' in fileinfo['people']:
            return fileinfo['people']['haspeople']
    return 0

def main():
    global photoinfo_directory, photolists_directory, max_links_per_file, max_photos, n, skip
    photo_counter = 0
    link_counter = 0
    u = codecs.open('%s%s%d.txt' % (photoinfo_directory, 'list_of_download_urls_', photo_counter+1), 'wt', 'utf-8')
    for file in iterate_photos_directory(photolists_directory):
        photos = read_Photos(file)
        for photo in photos:
            try:
                exif = photo.getExif()      #APICALL (n times)
                time.sleep(1)
            except:
                exif = None
            try:
                info = photo.getInfo()      #APICALL (n times)
                time.sleep(1)
                furl = getPhotoFile(info)
                fname = getPhotoFilename(furl)
                if not photoinfo_directory.endswith('/'):
                    photoinfo_directory += '/'
                # write metadata file
                f = codecs.open('%s%s.txt' % (photoinfo_directory, fname), 'wt', 'utf-8')
                f.write(furl)
                f.write('\n')
                j = exiftojson(exif)
                f.write(j)
                f.write('\n')
                t = infototags(info)
                f.write(str(t))
                f.write('\n')
                s = infotosubtitles(info)
                f.write(str(s))
                f.write('\n')
                l = infotolocation(info)
                f.write(str(l))
                f.write('\n')
                p = infotopeople(info)
                f.write(str(p))
                f.write('\n')
                f.close()
                u.write(furl)
                u.write('\n')
                photo_counter += 1
                link_counter += 1
                if link_counter >= max_links_per_file:
                    u.close()
                    u = codecs.open('%s%s%d.txt' % (photoinfo_directory, 'list_of_download_urls_', photo_counter+1), 'wt', 'utf-8')
                    link_counter = 0
            except IOError as (errno, strerror):
                sys.stderr.write("I/O error({0}): {1}\n".format(errno, strerror))
                sys.stderr.write('Error with photo %s (owner: %s)\n' % (photo.id, photo.owner_nsid))
                continue
            except flickr_api.base.FlickrAPIError:
                sys.stderr.write('API Error with photo %s (owner: %s)\n' % (photo.id, photo.owner_nsid))
                continue
            except:
                sys.stderr.write('Any Error')
                continue
            if photo_counter >= max_photos:
                break
        if photo_counter >= max_photos:
            break
    u.close()
    print flickr_api.method_call.APICOUNTER


if __name__ == "__main__":
    main()
