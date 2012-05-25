"""This scripts downloads images from Flickr servers using rotation user agent string"""

listpath = 'flickr_photos_test/infos/'
listfile = 'list_of_download_urls_1.txt'
destpath = 'flickr_photos_test/photos/'

listfiles = [ 'list_of_download_urls_1.txt', 'list_of_download_urls_1001.txt',
              'list_of_download_urls_2001.txt', 'list_of_download_urls_3001.txt' ]


import urllib
import random
import time


user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; de) Opera 11.51',
]

class MyURLOpener(urllib.FancyURLopener, object):
    version = random.choice(user_agents)


def download(url, destination_path):
    myopener = MyURLOpener()
    if not destination_path.endswith('/'):
        destination_path += '/'
    filename = url.rpartition('/')[2]
    try:
        myopener.retrieve(url, '%s%s' % (destination_path, filename))
    except IOError as (errno, strerror):
        sys.stderr.write('I/O error({0}): {1})'.format(errno, strerror))


def read_url_list_from_file(path, file):
    if not path.endswith('/'):
        path += '/'
    f = open( '%s%s' % (path, file), 'rt')
    for url in f:
        url = url.strip('\n')
        yield url
    f.close


for xlistfile in listfiles:
    for url in read_url_list_from_file(listpath, xlistfile):
        download(url, destpath)
        time.sleep(random.randint(1,5))
    time.sleep(1800)
