import os

infospath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos/infos'
#infospath = '/Users/henne/research_data/LocrFlickr_datasets1/flickr-files/flickr_photos_mobile/infos'

dlist = set()

for f in os.listdir(infospath):
    if f.lower().startswith('list_of_download_urls_'):
        myfile = open(os.path.join(infospath, f), 'rt')
        for url in myfile:
            filename = url.rpartition('/')[2].strip('\n')
            dlist.add(filename)

