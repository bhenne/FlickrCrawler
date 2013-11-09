import os

import Flickr20CheckDataset

dir_with_files_each_containing_list_of_photos_of_a_user = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos_mobile'
n = 1

print "we have %s photos with an info file" % len(Flickr20CheckDataset.photos_with_infos)

photo_owner = {}  #: map photo id -> owner id
for f in os.listdir(dir_with_files_each_containing_list_of_photos_of_a_user):
    if f.lower().endswith('.csv') and f.upper().find('-AT-') > 0:
        uid = f.rpartition('.')[0].replace('-AT-', '@')
        f = open(os.path.join(dir_with_files_each_containing_list_of_photos_of_a_user, f), 'rt')
        l = 0
        while l < n:
            line = f.readline()
            try:
                owner, id, secret, farm, server, title = line.split(';')
                photo_owner['%s' % (id)] = owner
            except ValueError:
                pass
            l += 1
        #if uid != owner:
        #    print "mismatch", uid, owner

photo_with_infos_owners = {}  #: copy of Flickr20CheckDataset.photos_with_infos for all having an photo->owner mapping
owners = {}   #: how often a user is an photo owner for all photos with infos
for p in Flickr20CheckDataset.photos_with_infos:
    pid = p.split('_')[0]
    if pid in photo_owner:
        photo_with_infos_owners[pid] = photo_owner[pid]
        if photo_owner[pid] in owners:
            owners[photo_owner[pid]] = owners[photo_owner[pid]] + 1
        else:
            owners[photo_owner[pid]] = 1

print " these photos have %s different owners" % len(owners)

for o in owners.keys():
    if owners[o] > 1:
        print "  this owner ccured %s times!" % owners[o]

if len(owners) == len(Flickr20CheckDataset.photos_with_infos):
    print "EVERYTHING IS FINE."
