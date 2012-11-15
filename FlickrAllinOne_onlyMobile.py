#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import re
import urllib
import random
import os
import sys
import time
import sqlite3
sys.path.insert(0,"python-flickr-api")
import flickr_api       #APICALL (once)
import json


dbfile = '/home/henne/crawled_data/Flickr/FlickrPhoto_onlyMobile.db'
photo_file_path = '/home/henne/crawled_data/Flickr'

# slow down crawler to respect limit of 1 api call per second
sleeptime = 0.33


########## INPUT DATA ##########
###### Webpages to crawl #######

flickr_pages_with_usernames_multiple = [
    'http://www.flickr.com/explore/',
    'http://www.flickr.com/explore/interesting/7days/',
    'http://www.flickr.com/galleries/',
    'http://www.flickr.com/photos/'
]

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
#fpwumm_cats = ['', 'recent', 'portrait', 'macro', 'night','landscape']
#fpwumm_cats = ['recent', '']
fpwumm_cats = ['recent']
fpwumm_ids = [ '72157623237412006', #Evo 4G
               '72157623257214966', #Droid Incredible
               '72157625301186015', #Droid Incredible 2
               '72157607417678583', #Droid Dream
               '72157629104662492', #One X
               '72157624762157476', #Desire HD
               '72157623390292511', #Desire 
               '72157624580560158', #Evo Shift 4G
               '72157624172742253', #iPhone 4
               '72157627469395877', #iPhone 4s
               '72157620775652629', #iPhone 3GS
               '72157607254796933', #iPhone 3G
               '72157626485419110', #Galaxy S2
               '72157623985657132', #Galaxy S
               '72157627776523729', #Galaxy Nexus
               '72157625948639270', #Galaxy Ace
               '72157625743838619', #Galaxy S 4G
               '72157624297372018', #Galaxy Epic 4G
               '72157629348324157', #Lumia 900
               '72157627740135087', #Lumia 800
               '72157626728398240',
               '72157616953691070',
               '72157623910717049',
               '72157621576215677',
               '72157603345296678',
               '56150',
               '53774',
               '50645',
               '55698',             #HTC Hero
               '72157617917812625', #HTC Hero 200
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
               '72157627540171397', #Droid Razr
               '72157624455893065', #Droid X
               '72157625729544791',
               '72157626931643196',
               '72157625348586031',
               '72157625577590052', #Xperia Arc
               '261',
               '72157623462273606',
               '157',
               '72157624225311271',
               '1869',
               '650',
               '5649',
               '1709',
               '72157623227400843',
               '72157624013405932', #Nokia N8
               '53218',
               '72157604507279486' ]
for cid in fpwumm_ids:
    for pcat in fpwumm_cats:
        flickr_pages_with_usernames_multiple_mobile.append('http://www.flickr.com/cameras_model_fragment.gne?src=js&id=%s&category=%s' % (cid, pcat))

def dates(year=2011, months=[1,12]):
    thedates = []
    def gen(m, days):
        for d in xrange(1, days+1):
            thedates.append('%02d/%02d/%02d' % (year, m, d))
    for month in xrange(months[0], months[1]+1):
        if month == 2:
            gen(month, 28)
        elif month in (1, 3, 5, 7, 8, 10, 12):
            gen(month, 31)
        else:
            gen(month, 30)
    return thedates

flickr_pages_with_usernames_once = []
page_range=[1,10]
years=[2011]
for year in years:
    for d in dates(year=year):
        for page in xrange(page_range[0],page_range[1]+1):
            flickr_pages_with_usernames_once.append('http://www.flickr.com/explore/interesting/%s/page%s' % (d, page))
for d in dates(year=2012, months=[1,5]):
    for page in xrange(page_range[0],page_range[1]+1):
        flickr_pages_with_usernames_once.append('http://www.flickr.com/explore/interesting/%s/page%s' % (d, page))
for d in dates(year=2010, months=[12,12]):
    for page in xrange(page_range[0],page_range[1]+1):
        flickr_pages_with_usernames_once.append('http://www.flickr.com/explore/interesting/%s/page%s' % (d, page))

################################


def debug(str):
    sys.stdout.write('%s\n' % str)
    sys.stdout.flush()

def error(str):
    sys.stderr.write('%s\n' % str)
    sys.stderr.flush()
    

### 1. PERSONALIZED URLS


def check_personalized_urls_table(dbconn):
    """Check if table personalized_urls exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from personalized_urls')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('CREATE TABLE personalized_urls (purl VARCHAR(128), direct_photo_id VARCHAR(20), mobile BOOLEAN, status INT DEFAULT 0, PRIMARY KEY (purl) ON CONFLICT IGNORE)')
    dbcursor.close()

def personalized_urls_from_file(dbconn, mobile=False, path='', filename='flickr_usernames.txt'):
    """Read personalized urls from file and store them in table personalized_urls."""

    dbcursor = dbconn.cursor()
    userfile = codecs.open('%s%s' % (path, filename), 'r', 'utf-8')
    m = 0 if mobile==False else 1
    for userline in userfile:
        p = userline.strip()
        dbcursor.execute('INSERT INTO personalized_urls VALUES (?,?,?)', [p,m,0])
    dbconn.commit()
    dbcursor.close()

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
    """URLopener with random user agent."""
    version = random.choice(user_agents)

work_on_all = []
def personalized_urls_from_web_all(dbconn, url_list, mobile=False, wait_interval=[1,3]):
    """Crawl personalized urls from web pages and store them in table personalized_urls AND Get all from list instead of random_choices."""

    global work_on_all
    if len(work_on_all) == 0:
        debug('START AGAIN _from_web_all() with %s urls' % len(url_list))
        work_on_all = list(url_list)
    #work_on_all = url_list
    try:
      personalized_urls_from_web(dbconn, [work_on_all.pop()], mobile=mobile, crawls=1, wait_interval=wait_interval)
    except IndexError:
      return

def personalized_urls_from_web(dbconn, url_list, mobile=False, crawls=1, wait_interval=[30,180]):
    """Crawl personalized urls from web pages and store them in table personalized_urls."""

    def parse_personalized_urls(url):
        """Parse a single web page given by its url for personalized urls."""
        debug('parsing %s' % url)
        myopener = MyURLOpener()
        page = myopener.open(url)
        pagestring = page.read()
        theset = []
        blacklist = [ 'tags', 'upload', 'organize']
        splits = re.split('href="/photos/', pagestring)
        for i in xrange(1, len(splits)):
            userAndPhoto = splits[i].partition('/"')[0]
            if userAndPhoto.count('/') == 1:
                sp = userAndPhoto.partition('/')
                maybe = [ sp[0], sp[2] ]
            else:
                continue
            if maybe[0] not in blacklist and len(maybe[0]) > 0 and maybe[0][0] not in [ '"', "'"] and maybe[0] not in theset:
                theset.append(maybe)
        debug('  got %s' % theset)
        return theset

    dbcursor = dbconn.cursor()
    m = 0 if mobile==False else 1
    status = 0
    for i in xrange(0, crawls):
        resultset = parse_personalized_urls(random.choice(url_list))
        for p in resultset:
            dbcursor.execute('INSERT INTO personalized_urls VALUES (?,?,?,?)', [p[0],p[1],m,status])
        dbconn.commit()
        if i < crawls-1: 
            time.sleep(random.randint(*wait_interval))
    dbcursor.close()

def get_personalized_urls(dbconn, mobile=None, status=None, all_columns=False, limit=None):
    """Get personalized urls from table personalized_urls with optional filters.
    @param mobile: True for mobile users, False for others
    @param status: status number. 0 nothing done. 1 person info retrieved. 2 basic photo info retrieved. 3 downloaded file and metadata.
    @param all_columns: False: return only personalized url. True: return all from table.
    @param limit: limit number of results. None mean no limit.
    """

    if all_columns == False:
        q = 'SELECT purl FROM personalized_urls WHERE 1=1'
    else:
        q = 'SELECT purl, direct_photo_id, mobile, status FROM personalized_urls WHERE 1=1'
    if (mobile is not None):
        q += ' AND mobile=0' if mobile==False else ' AND mobile=1'
    if (status is not None):
        q += ' AND status=%s' % status
    if (limit is not None):
        q += ' LIMIT %s' % limit
    dbcursor = dbconn.cursor()
    dbcursor.execute(q)
    all = dbcursor.fetchall() 
    dbcursor.close()
    return all

def print_personalized_urls(dbconn, mobile=None, status=None, limit=None):
    """Print personalized urls from table personalized_urls got with optional filters.

    @see get_personalized_urls for parameters"""

    for pu in get_personalized_urls(dbconn, mobile=mobile, status=status, all_columns=True, limit=limit):
        print pu

def remove_purl_from_db(dbconn, rm_purl):
    """Remove row of purl rm_purl from db"""
    dbcursor = dbconn.cursor()
    dbcursor.execute('DELETE from personalized_urls WHERE purl=?', [rm_purl])
    dbconn.commit()
    dbcursor.close()


### USER INFOS, RETRIEVED VIA PERSONALIZED URLS


def check_user_info_table(dbconn):
    """Check if table user_infos exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from user_infos')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('''
                           CREATE TABLE user_infos (
                           path_alias VARCHAR(128),
                           username VARCHAR(128), 
                           realname VARCHAR(128), 
                           is_pro BOOLEAN, 
                           id VARCHAR(20), 
                           nsid VARCHAR(20), 
                           location VARCHAR(128), 
                           photo_count INTEGER, 
                           photo_firstdate DATETIME,
                           photo_firstdatetaken DATETIME,
                           PRIMARY KEY (nsid)
                           ON CONFLICT REPLACE)
                           ''')
    dbcursor.close()

def api_get_user_info(dbconn, personalized_url):
    """Retrieve user information via Flickr API."""

    p = {}
    person = None
    try:
        person = flickr_api.Person.findByUrl('http://www.flickr.com/photos/%s' % personalized_url)    #APICALL
        time.sleep(sleeptime)
        person.load()      #APICALL
        time.sleep(sleeptime)
        for i in [ 'path_alias', 'username', 'realname', 'ispro', 'id', 'nsid', 'location' ]:
            if i in person.__dict__:
                p[i] = unicode(person[i])
            else:
                p[i] = u''
        for i in [ 'count', 'firstdate', 'firstdatetaken' ]:
            if i in person['photos_info'].keys():
                p['p_'+i] = unicode(person['photos_info'][i])
            else:
                p['p_'+i] = u''
        return p
    except flickr_api.flickrerrors.FlickrAPIError as api_error:
        if api_error.message.lower().find('user not found') > -1:
            remove_purl_from_db(dbconn, personalized_url)
            error('REMOVED personalized url %s (reason: user does not exist (anymore))' % personalized_url)
    except:
        print(u'Error at getting user info for: %s' % personalized_url)
        #if person is not None:
        #    for i in person.__dict__:
        #        print( u' %s:%s' % (i, person[i.decode('utf-8', 'replace')]))
    return None

def download_user_infos(dbconn, personalized_urls):
    """Download user information via API for a list of personalized urls."""

    dbcursor = dbconn.cursor()
    for q in personalized_urls:
        p = q[0]
        i = api_get_user_info(dbconn, p)
        if i is None:
            continue
        i['path_alias'] = p     # replace unneeded path_alias by personalized url to join purls table
        debug('dl user info purl %s' % i['nsid'])
        dbcursor.execute('''REPLACE INTO user_infos (path_alias, username, realname, is_pro, id, nsid, 
                         location, photo_count, photo_firstdate, photo_firstdatetaken) VALUES 
                         (:path_alias,:username,:realname,:ispro,:id,:nsid,
                         :location,:p_count,:p_firstdate,:p_firstdatetaken)
                         ''', i)
        dbcursor.execute('UPDATE personalized_urls SET status=1 WHERE purl=?', [p])
    dbconn.commit()
    dbcursor.close()

def get_user_infos(dbconn, status=None, limit=None):
    """Get user information from table user_infos with filters.

    @param status: None: all entries; otherwise integer as status id.
    @param limit: limit number of results."""

    if (status is None):
        s = ''
    else:
        s = ' JOIN personalized_urls WHERE user_infos.path_alias=personalized_urls.purl AND status=%s' % status
    if (limit is None):
        l = ''
    else:
        l = ' LIMIT %s' % limit
    q = '''SELECT nsid, id, path_alias, username, realname, is_pro, location, 
        photo_count, photo_firstdate, photo_firstdatetaken FROM user_infos%s%s
        ''' % (s, l)
    dbcursor = dbconn.cursor()
    dbcursor.execute(q)
    all = dbcursor.fetchall() 
    dbcursor.close()
    return all

def print_user_infos(dbconn, status=None, limit=None):
    """Print user information from table user_infos with filters.

    @see get_user_infos for parameters."""

    for i in get_user_infos(dbconn, status=status, limit=limit):
        print i

def remove_user_info_from_db(dbconn, rm_nsid):
    dbcursor = dbconn.cursor()
    dbcursor.execute('DELETE from user_infos WHERE nsid=?', [rm_nsid])
    dbconn.commit()
    dbcursor.close()
    

### BASIC PHOTO DATA
### PHOTOS per user ### we only take one per user


def check_photos_table(dbconn):
    """Check if table photos exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from photos')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('''CREATE TABLE photos (nsid VARCHAR(20), 
                                                   photo_id VARCHAR(20), 
                                                   photo_secret INT,
                                                   photo_farm INT,
                                                   photo_server INT,
                                                   title VARCHAR(256),
                                                   PRIMARY KEY (nsid, photo_id) ON CONFLICT ABORT)''')
    dbcursor.close()

def api_get_user_photo(dbconn, a_user_info):
    """Retrieve basic photo information for one photo via Flickt API."""

    debug('dl basic photo info user %s' % a_user_info[0]) 
    p = flickr_api.Person(username=a_user_info[3], ispro=(a_user_info[5]=='True'), realname=a_user_info[4],
                          path_alias=a_user_info[2], id=a_user_info[1], nsid=a_user_info[0], location=a_user_info[6],
                          p_count=a_user_info[7], p_firstdate=a_user_info[8], p_firstdatetaken=a_user_info[9])
    photos = []
    try:
        photos = p.getPublicPhotos()       #APICALL (n times)
    except:
        sys.stderr.write('Error with Person %s' % a_user_info[0])
    time.sleep(sleeptime)
    dbcursor = dbconn.cursor()
    # Check if user has photos, if not, completely remove user info/purl from dataset
    if len(photos) == 0:
        remove_purl_from_db(dbconn, a_user_info[2])
        remove_user_info_from_db(dbconn, a_user_info[0])
        error('REMOVED user nsid:%s with personalized url %s from dataset (reason: user has no public photos now)' % (a_user_info[0], a_user_info[2]))
        return None
    # check for direct_photo_id, mobile, status FROM personalized_urls WHERE 1=1
    try:
      dbcursor.execute('''SELECT direct_photo_id from personalized_urls where purl=?''', [a_user_info[2]])
      dpid = dbcursor.fetchone()[0]
      x = flickr_api.Photo(id=dpid)
      x.load()
    except:
      x = photos[0]
    dbcursor.execute('''REPLACE INTO photos (nsid, photo_id, photo_secret, photo_farm, photo_server, title) 
                     VALUES (?,?,?,?,?,?)
                     ''',         [a_user_info[0], x['id'], x['secret'], x['farm'], x['server'], x['title']])
    dbcursor.execute('UPDATE personalized_urls SET status=2 WHERE purl=?', [a_user_info[2]])


def download_photos(dbconn, user_infos):
    """Download a list of one photo per user."""
    dbcursor = dbconn.cursor()
    for user_info in user_infos:
        api_get_user_photo(dbconn, user_info)
    dbconn.commit()
    dbcursor.close()

def get_photos(dbconn, status=None, limit=None):
    """Get photos from photos table with optional filters.
    @param status: status number. 0 nothing done. 1 person info retrieved. 2 basic photo info retrieved. 3 downloaded file and metadata.
    @param limit: limit number of results. None mean no limit.
    """

    if (status is None):
        s = ''
    else:
        s = ' JOIN user_infos ON photos.nsid=user_infos.nsid JOIN personalized_urls ON (user_infos.path_alias=personalized_urls.purl) AND status=%s' % status
    if (limit is None):
        l = ''
    else:
        l = ' LIMIT %s' % limit

    dbcursor = dbconn.cursor()
    dbcursor.execute('select photos.nsid, photo_id, photo_secret, photo_farm, photo_server, title from photos%s%s' % (s, l))
    all = dbcursor.fetchall() 
    dbcursor.close()
    return all

def print_photos(dbconn):
    """Print all photos from photos table"""
    for p in get_photos(dbconn):
        print p

def remove_photos_of_user_from_db(dbconn, rm_nsid):
    """Remove photo of user with nsid rm_nsid from photo table."""
    dbcursor = dbconn.cursor()
    dbcursor.execute('DELETE from photos WHERE nsid=?', [rm_nsid])
    dbconn.commit()
    dbcursor.close()


### PHOTO DETAILS


def check_photo_infos_table(dbconn):
    """Check if table photo_infos exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from photo_infos')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('''CREATE TABLE photo_infos (photo_id VARCHAR(20), 
                                                        json_photo_info TEXT,
                                                        PRIMARY KEY (photo_id) ON CONFLICT ABORT)''')
    dbcursor.close()

def check_photo_exifs_table(dbconn):
    """Check if table photo_infos exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from photo_exifs')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('''CREATE TABLE photo_exifs (photo_id VARCHAR(20), 
                                                        json_photo_exif TEXT,
                                                        PRIMARY KEY (photo_id) ON CONFLICT ABORT)''')
    dbcursor.close()

def check_photo_url_table(dbconn):
    """Check if table photo_infos exists, otherwise create it."""

    dbcursor = dbconn.cursor()
    try:
      dbcursor.execute('select * from photo_urls')
    except sqlite3.OperationalError as e:
      if str(e).startswith('no such table'):
          dbcursor.execute('''CREATE TABLE photo_urls (photo_id VARCHAR(20), 
                                                       url TEXT,
                                                       dlstatus INT default 0,
                                                       PRIMARY KEY (photo_id) ON CONFLICT ABORT)''')
    dbcursor.close() 

def flickr_api_photo_get_info_to_dict(info):
    """Transform output of flickr_api.getInfo() to a dict.
    
    Returned dict is transformable to json via json.dumps."""

    if type(info) == dict:
        d = {}
        for k, v in info.items():
            d[k] = flickr_api_photo_get_info_to_dict(v)
        return d
    elif type(info) == list:
        l = []
        for i in info:
            l.append(flickr_api_photo_get_info_to_dict(i))
        return l
    elif isinstance(info, flickr_api.Person):
        return flickr_api_photo_get_info_to_dict(info.__dict__)
    elif isinstance(info, flickr_api.Tag):
        return flickr_api_photo_get_info_to_dict(info.__dict__)
    elif str(type(info)).find('flickr_api.objects.Note') > -1:
        #type/isinstance of does not work, why not?
        return flickr_api_photo_get_info_to_dict(info.__dict__)
    elif type(info) in [str, unicode, int, long, float, bool]:
        return info
    elif info is None:
        return None
    else:
        error('TODO? type %s not properly converted?' % type(info))
        return unicode(info)

def flickr_api_photo_exif_to_dict(exif):
    """Transform output of flickr_api.getExif() to a dict.
    
    Returned dict is transformable to json via json.dumps."""

    blacklist = ['loaded', 'label', 'tagspaceid']
    e = []
    if type(exif) == list:
        for t in exif:
            #e[i['tag']] = i.__dict__['raw']
            tmp = t.__dict__
            for f in blacklist:
                if f in tmp:
                    del tmp[f]
            e.append(tmp)
    return e

def download_file(url, destination_path):
    """Download file from url to destination_path."""
    myopener = MyURLOpener()
    if not destination_path.endswith('/'):
        destination_path += '/'
    try:
        filename = url.rpartition('/')[2]
        myopener.retrieve(url, '%s%s' % (destination_path, filename))
    except IOError as (errno, strerror):
        error('!! I/O error({0}): {1})'.format(errno, strerror))
        return False
    except:
        error('Error downloading URL %s' % url)
        return False
    return True

def api_retrieve_metadata_and_download_file(dbconn, photo):
    """Download photo file. Retrieve Info and Exif for photo."""

    def getPhotoFile(photoinfo, noOriginal='b'):
        try:
          if 'originalsecret' in photoinfo and 'originalformat' in photoinfo:
              return 'http://farm%s.static.flickr.com/%s/%s_%s_o.%s' % (photoinfo['farm'], photoinfo['server'], 
                                                                         photoinfo['id'], photoinfo['originalsecret'], 
                                                                         photoinfo['originalformat'])
          else:
              return 'http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg' % (photoinfo['farm'], photoinfo['server'], 
                                                                           photoinfo['id'], photoinfo['secret'], noOriginal)
        except:
          return None
    
    def getPhotoFilename(photofileURL):
        return photofileURL.rpartition('/')[2]
    
    def exiftojson(exif, sort_keys=True):
        """Tranforms a Flickr Exif object to a JSON string"""
        if exif is None:
            return ''
        e = [x.__dict__ for x in exif]
        return json.dumps(e, sort_keys=sort_keys)

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

    p = flickr_api.Photo(owner_nsid=photo[0], id=photo[1], secret=photo[2],
                      farm=int(photo[3]), server=int(photo[4]), title=photo[5])
    debug('dl info/exif for photo %s of user %s' % (photo[1], photo[0]))
    perror = None
    try:
      exif = p.getExif()      #APICALL
      time.sleep(sleeptime)
    except:
      exif = None
    try:
      info = p.getInfo()      #APICALL
      time.sleep(sleeptime)
    except flickr_api.flickrerrors.FlickrAPIError as api_error:
      info = None
      if api_error.message.lower().find('not found') > -1:
        perror = api_error.message
        error('owner %s photo %s: %s:' % (photo[0], photo[1], perror))
    furl = getPhotoFile(info)
    #print exiftojson(exif)
    #print infototags(info)
    #print infotosubtitles(info)
    #print infotolocation(info)
    #print infotopeople(info)
    json_info = json.dumps(flickr_api_photo_get_info_to_dict(info), sort_keys=True)
    json_exif = json.dumps(flickr_api_photo_exif_to_dict(exif), sort_keys=True)
    
    debug('dl photo w/id %s' % photo[1])
    dbcursor = dbconn.cursor()
    #dbcursor.execute('''SELECT mobile from personalized_urls JOIN user_infos ON 
    #                 (personalized_urls.purl=user_infos.path_alias) JOIN photos ON 
    #                 (user_infos.nsid=photos.nsid) where photo_id=?''', [photo[1]])

    dbcursor.execute('''SELECT mobile FROM 
                     photos JOIN user_infos ON (user_infos.nsid=photos.nsid) 
                     JOIN personalized_urls ON (user_infos.path_alias=personalized_urls.purl) 
                     WHERE photo_id=?''', [photo[1]])
    try:
      subpath = 'm2/'
    except TypeError:
      perror = "SELECT returned empty set (None)."
    if (perror is None) and (download_file(furl, '%s/%s' % (photo_file_path, subpath)) == True):
        dbcursor.execute('''REPLACE INTO photo_urls (photo_id, url, dlstatus) VALUES 
                         (?, ?, ?)''', [photo[1], furl, 1])
        dbcursor.execute('''REPLACE INTO photo_infos (photo_id, json_photo_info) VALUES 
                         (?, ?)''', [photo[1], json_info])
        dbcursor.execute('''REPLACE INTO photo_exifs (photo_id, json_photo_exif) VALUES 
                         (?, ?)''', [photo[1], json_exif])   
        dbcursor.execute('''UPDATE personalized_urls SET status=3 WHERE purl=
                         (SELECT path_alias from user_infos where nsid=?)''', [photo[0]])
    else:
        # photo_infos, photo_exifs, photo_urls will not be updated
        # and now delete purl, user_info and photo
        dbcursor.execute('''SELECT path_alias from user_infos where nsid=?''', [photo[0]])
        purl = dbcursor.fetchone()[0]
        remove_purl_from_db(dbconn, purl)
        remove_user_info_from_db(dbconn, photo[0])
        remove_photos_of_user_from_db(dbconn, photo[0])
        error('REMOVED personalized url %s, info about user %s and basic photo information for photo %s (reason: photo file missing)' % (purl, photo[0], photo[1]))
    dbconn.commit()
    dbcursor.close()
    
def download_metadata_and_photos(dbconn, photos):
    """Downloads extended photo information/metadata for a list of photos.
    
    @param photos: list of photos (basic photo infos) as returned by get."""

    for photo in photos:
        api_retrieve_metadata_and_download_file(dbconn, photo)
#

##############################################
#################### MAIN ####################


interrupt_now = False
def interrupt(signal, frame):
    global interrupt_now
    interrupt_now = True
    debug('PROGRAM INTERRUPTED')

def init(dbconn):
    """Check db tables and creates them if not exist."""
    check_personalized_urls_table(dbconn)
    check_user_info_table(dbconn)
    check_photos_table(dbconn)
    check_photo_infos_table(dbconn)
    check_photo_exifs_table(dbconn)
    check_photo_url_table(dbconn)

def main():
    """The main loop."""

    # stop crawling using: kill -SIGUSR1 `ps -eo "%p%a" |grep "python FlickrAllinOne.py"|grep -v grep|cut -f 2 -d " "`
    import signal
    signal.signal(signal.SIGUSR1, interrupt)

    time_start = time.time()

    dbconn = sqlite3.connect(dbfile)
    init(dbconn)

    limit=50
    quit=0
    while 42:

        if interrupt_now == True: break
        # DOWNLOADING USER INFORMATION, set status=1
        p = get_personalized_urls(dbconn, status=0, limit=limit)
        if len(p) == 0:
          quit += 1
        # use with "quit > 1", if purl-prefilled db should be emptied and script stopped afterwards
        if quit > quit:
            debug('Exiting ... (reason: %s times we had no personalized urls)' % quit)
            break
        download_user_infos(dbconn, p)
        #print_user_infos(dbconn)

        if interrupt_now == True: break
        # DOWNLOAD BASIC DATA FOR EACH PHOTO w/status=1
        download_photos(dbconn, get_user_infos(dbconn, status=1, limit=None))
        #print_photos(dbconn)
 
        if interrupt_now == True: break
        # DOWNLOAD PHOTO, EXIF AND INFOS
        download_metadata_and_photos(dbconn, get_photos(dbconn, status=2, limit=None))

        if interrupt_now == True: break 
        # GET USER PERSONALIZED URLS/NDIS URLS, status=0
#        personalized_urls_from_web(dbconn, flickr_pages_with_usernames_multiple_mobile, mobile=True, crawls=1, wait_interval=[1,3]) #60-1800
        personalized_urls_from_web_all(dbconn, flickr_pages_with_usernames_multiple_mobile, mobile=True, wait_interval=[1,3]) #60-1800
        #print_personalized_urls(dbconn, mobile=True, status=0)
        time.sleep(2)

        time_used = time.time() - time_start
        api_calls = flickr_api.method_call.call_counter
        debug('%s %s %s' % (time_used, api_calls, api_calls/time_used))
        
    dbconn.close()


if __name__ == '__main__':
    main()
