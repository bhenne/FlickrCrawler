import os

imagepath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos/photos'
#imagepath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos_mobile/photos'
infospath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos/infos'
#infospath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos_mobile/infos'

import Flickr19GetSelection
def filtered(filename):
    #return (filename not in Flickr19GetSelection.dlist)
    return False

photos = set()
for name in os.listdir(imagepath):
    if name.split('.')[-1] in ('jpg', 'jpeg') and filtered(name) == False:
       photos.add(name) 
    o = False
    if name.rpartition('.')[0][-1:] == 'o':
        o = True    #: Flickr original file with embedded metadata

print "photos: %s" % len(photos)

photos_with_infos = set()
for name in os.listdir(infospath):
    if name.endswith('.txt') and name.split('.')[-2] in ('jpg', 'jpeg'):
        jpgname = name.split('.txt')[0]
        if jpgname in photos:
            photos_with_infos.add(jpgname) 

print "photos with infos: %s" % len(photos_with_infos)
