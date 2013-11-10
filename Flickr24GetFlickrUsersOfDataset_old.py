"""outputs photo owners of old datasets with csv files w/o sqlite data"""

import Flickr21CheckUser_1to1

for owner in sorted(Flickr21CheckUser_1to1.photo_with_infos_owners.values()):
    print owner
