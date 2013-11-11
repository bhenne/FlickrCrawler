"""outputs photos of old datasets with csv files w/o sqlite data"""

import Flickr20CheckDataset

for photo in sorted(Flickr20CheckDataset.photos_with_infos):
    print photo
