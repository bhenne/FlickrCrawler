# check exif in info files of older crawls for the existence of exif data
#  -> we do this to verify old datasets, while we cannot use Flickr API to 
#     check if access denied more than one year later

import os
import codecs
import Flickr20CheckDataset   # configure paths here!

infospath = Flickr20CheckDataset.infospath
count = len(Flickr20CheckDataset.photos_with_infos)

none = 0
empty = 0
progress = 0
for p in Flickr20CheckDataset.photos_with_infos:
    f = codecs.open(os.path.join(infospath, '%s.txt' % p), 'rt', 'utf-8')
    url, exifjson, tags, subtitles, location, people = f.readlines()
    exifjson = exifjson.strip('\n')
    if exifjson == '':
        none += 1
    elif exifjson == '[]':
        empty += 1
    elif len(exifjson) < 100:
        print '<%s>' % exifjson
    f.close()
    progress += 1
    if progress % round(count/50.0, 0) == 0:
        print round(100.0/count*progress, 1), '%'

print "none=denied: %s (%s %%), empty: %s (%s %%)" % (none, round(100.0/count*none, 1), empty, round(100.0/count*empty, 1))
