"""This script reads Photos from each crawled users Photos file and retrieves n Photos file URLs, Exif information and tags.
"""


n = 1                       # retrieve n photos
skip = 0                    # skip the first skip photos, maybe at a second run
max_photos= 20000           # stop if max_photos photos retrieved

photolists_directory = 'flickr_photos/'
photoinfo_directory  = 'flickr_photos/infos/'


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

def main():
    global photoinfo_directory, photolists_directory, max_links_per_file, max_photos, n, skip
    photo_counter = 0
    exif_denied_counter = 0
    exif_ok = 0
    exif_no = 0
    link_counter = 0
    u = codecs.open('%s%s%d.txt' % (photoinfo_directory, 'list_of_download_urls_', photo_counter+1), 'wt', 'utf-8')
    outfile = codecs.open('flickr_data/Flickr_exif_denied_list.txt', 'wt', 'utf-8')
    for file in iterate_photos_directory(photolists_directory):
        photos = read_Photos(file)
        for photo in photos:
            exif = 42
            try:
                exif = photo.getExif()      #APICALL (n times)
                time.sleep(0.8)
            except:
                exif = None
            if exif == None:
                exif_denied_counter += 1
                outfile.write('%s;%s;%s\n' % (photo.owner_nsid, 'denied', sys.exc_info()[1]))
            elif len(exif) > 0:
                exif_ok += 1
                outfile.write('%s;%s;%s\n' % (photo.owner_nsid, 'not-empty', len(exif)))
            else:
                exif_no += 1
                outfile.write('%s;%s;%s\n' % (photo.owner_nsid, 'empty', ''))
            photo_counter += 1
            print exif_denied_counter, exif_ok, exif_no
            if photo_counter >= max_photos:
                break
        if photo_counter >= max_photos:
            break
    u.close()
    outfile.close()
    print exif_denied_counter, exif_ok, exif_no
    f = open('flickr_data/Flickr_exif_denied.txt', 'wt')
    f.write('denied, ok, no = %s, %s, %s' % (exif_denied_counter, exif_ok, exif_no))
    f.close()
    print flickr_api.method_call.APICOUNTER


if __name__ == "__main__":
    main()
