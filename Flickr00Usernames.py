#!/usr/bin/env python
"""This script crawls Flickr path_aliases/NSIDs from web pages without any API usage.

The script loads and parses different flickr web pages, which include /photos/FOO-URLs
and grabs them. Names can be used to retrieve Persons via API using getByUrl.
Names may not be uniq. Used sort/uniq at bash to filter.
Names are finally stored in FlickrUsernames.uniq.txt and FlickrUsernamesMobile.uniq.txt
"""

import re, urllib, random, os, sys, time

user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:7.0.1) Gecko/20100101 Firefox/7.0.1',
    'Mozilla/5.0 (X11; Linux i686; rv:6.0) Gecko/20100101 Firefox/6.0',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.80 (Windows NT 6.1; U; es-ES) Presto/2.9.181 Version/12.00',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; de) Opera 11.51',
#    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
#    'Mozilla/4.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/5.0)',
#    'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
#    'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)',
#    'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.348; U; en) Presto/2.5.25 Version/10.54',
#    'Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (J2ME/23.377; U; en) Presto/2.5.25 Version/10.54',
#    'Mozilla/5.0 (BlackBerry; U; BlackBerry 9850; en-US) AppleWebKit/534.11+ (KHTML, like Gecko) Version/7.0.0.115 Mobile Safari/534.11+'
]

class MyURLOpener(urllib.FancyURLopener, object):
    version = random.choice(user_agents)

flickr_pages_with_usernames_once = []
flickr_pages_with_usernames_multiple = [
    'http://www.flickr.com/explore/',
    'http://www.flickr.com/explore/interesting/7days/',
    'http://www.flickr.com/galleries/',
    'http://www.flickr.com/photos/'
]
#fpwumm_cats = ['', 'recent', 'portrait', 'macro', 'night','landscape']
fpwumm_cats = ['recent']
fpwumm_ids = [ '72157623237412006', #Evo 4G
               '72157623257214966', #Droid Incredible
               '72157629104662492', #One X
               '72157624762157476', #Desire HD
               '72157623390292511', #Desire 
               '72157624172742253', #iPhone 4
               '72157627469395877', #iPhone 4s
               '72157620775652629', #iPhone 3GS
               '72157607254796933', #iPhone 3G
               '72157626485419110', #Galaxy S2
               '72157623985657132', #Galaxy S
               '72157627776523729', #Galaxy Nexus
               '72157625948639270', #Galaxy Ace
               '72157626728398240',
               '72157616953691070',
               '72157623910717049',
               '72157621576215677',
               '72157603345296678',
               '56150',
               '53774',
               '50645',
               '72157603328945228',
               '72157600292926652',
               '72157600767692957',
               '3255',
               '72157600291966813',
               '1022',
               '72157605294024642',
               '72157601810364683',
               '72157604583315619',
               '72157602768624982',
               '72157600767694317',
               '72157627540171397',
               '72157624455893065',
               '72157625729544791',
               '72157626931643196',
               '72157625348586031',
               '72157625577590052',
               '261',
               '72157623462273606',
               '157',
               '72157624225311271',
               '1869',
               '650',
               '5649',
               '1709',
               '72157623227400843',
               '72157624013405932',
               '53218',
               '72157604507279486' ]

flickr_pages_with_usernames_multiple_mobile = [
    'http://www.flickr.com/cameras/apple/iphone_4s/',
    'http://www.flickr.com/cameras/apple/iphone_4/',
    'http://www.flickr.com/cameras/apple/iphone_3gs/',
    'http://www.flickr.com/cameras/apple/iphone_3g/',
    'http://www.flickr.com/cameras/htc/evo4g/',
    'http://www.flickr.com/cameras/htc/droid_incredible/',
    'http://www.flickr.com/cameras/htc/desire_hd/',
    'http://www.flickr.com/cameras/htc/desire/',
    'http://www.flickr.com/cameras/htc/adr6400l/',
    'http://www.flickr.com/cameras/blackberry/9700/',
    'http://www.flickr.com/cameras/blackberry/8520/',
    'http://www.flickr.com/cameras/blackberry/rim__9800/',
    'http://www.flickr.com/cameras/blackberry/9300/',
    'http://www.flickr.com/cameras/blackberry/8900/',
    'http://www.flickr.com/cameras/blackberry/bbrim_8530/',
    'http://www.flickr.com/cameras/blackberry/9630/',
    'http://www.flickr.com/cameras/lg/ku990/',
    'http://www.flickr.com/cameras/lg/kf750/',
    'http://www.flickr.com/cameras/lg/vx-9700/',
    'http://www.flickr.com/cameras/lg/cu720/',
    'http://www.flickr.com/cameras/nokia/c3-00/',
    'http://www.flickr.com/cameras/nokia/n95/',
    'http://www.flickr.com/cameras/nokia/n8-00/',
    'http://www.flickr.com/cameras/nokia/e71/',
    'http://www.flickr.com/cameras/sonyericsson/lt15i/',
    'http://www.flickr.com/cameras/sonyericsson/k800i/',
    'http://www.flickr.com/cameras/sonyericsson/u20i/',
    'http://www.flickr.com/cameras/sonyericsson/seu5i/',
    'http://www.flickr.com/cameras/sonyericsson/c905/',
    'http://www.flickr.com/cameras/samsung/gt-i9000/',
    'http://www.flickr.com/cameras/samsung/samsung_gt-i9100/',
    'http://www.flickr.com/cameras/samsung/samsung_nexus_s/',
    'http://www.flickr.com/cameras/samsung/sgh-t959v/',
]

for cid in fpwumm_ids:
    for pcat in fpwumm_cats:
        flickr_pages_with_usernames_multiple_mobile.append('http://www.flickr.com/cameras_model_fragment.gne?src=js&id=%s&category=%s' % (cid, pcat))


def dates(year=2011):
    thedates = []
    def gen(m, days):
        for d in xrange(1, days+1):
            thedates.append('%02d/%02d/%02d' % (year, m, d))
    for month in xrange(1, 13):
        if month == 2:
            gen(month, 28)
        elif month in (1, 3, 5, 7, 8, 10, 12):
            gen(month, 31)
        else:
            gen(month, 30)
    return thedates

#done: 2009:page1-4,2010:page1-6,2011:page1-5, at 26/10/2011
year=2010
suffix = ''
suffix = 'page6'
for d in dates(year=year):
    flickr_pages_with_usernames_once.append('http://www.flickr.com/explore/interesting/%s/%s' % (d, suffix))


def get_names(url, out=sys.stdout):
    sys.stderr.write('getting %s\n' % url)
    myopener = MyURLOpener()
    page = myopener.open(url)
    pagestring = page.read()
    theset = set()
    blacklist = [ 'tags', 'upload' ]
    splits = re.split('href="/photos/', pagestring)
    for i in xrange(1, len(splits)):
        maybe = splits[i].partition('/')[0]
        if maybe not in blacklist and maybe[0] not in [ '"', "'"]:
            theset.add(maybe)
    for e in theset:
        out.write('%s\n' % e)
        
### 1) any users ###
#for url in flickr_pages_with_usernames_once:
#    get_names(url)
#
#for i in xrange(0, 100):
#    get_names(random.choice(flickr_pages_with_usernames_multiple))

### 2) Mobile users ###
outfile=open('MobileUsers.txt', 'at')
for i in xrange(0, 50):
    for url in flickr_pages_with_usernames_multiple_mobile:
        get_names(url, out=outfile)
        time.sleep(random.randint(1,6))
    outfile.flush()
    os.fsync(outfile.fileno())
    time.sleep(random.randint(600,3600))
    
