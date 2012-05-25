"""This script uses flickr path_aliases/NSIDs to retrieve Flickr Person information.

The script loads flickr path_aliases/NSIDs from file after having been crawled by Flickr00Usernames.py
They  arr used to query Flickr API. People informatio are retrieved and stored as CVS in file.
See files flickr_users_unicode.txt and flickr_users_mobile_unicode.txt.
For output format of CSV see join statement of person_info.
"""

import sys
import flickr_api       #APICALL (once)
import pickle as pickle
import time
import codecs

path_aliases = []
persons = {}

def get_users_from_file(path='', filename='FlickrUsernamesTest.txt'):
    userfile = open('%s%s' % (path, filename), 'r')
    for userline in userfile:
        path_aliases.append(userline.strip())

def person_info(path_alias):
    p = {}
    person = persons[path_alias]
    # we do not use: iconfarm, iconserver
    for i in [ 'username', 'ispro', 'realname', 'path_alias', 'id', 'nsid', 'location'  ]:
        if i in person.__dict__:
            if type(i) != str:
                p[i] = unicode(str(person[i]))
            else:
                 p[i] = unicode(person[i])
        else:
            p[i] = u''
    for i in [ 'count', 'firstdate', 'firstdatetaken' ]:
        if i in person.photos.__dict__:
            p['p_'+i] = unicode(str(person.photos.__dict__[i]))
        else:
            p['p_'+i] = u''
    return u';'.join([ p['username'], str(p['ispro']), p['realname'], 
                       p['path_alias'], p['id'], p['nsid'], p['location'],
                       p['p_count'], p['p_firstdate'], p['p_firstdatetaken'] ])



f = codecs.open('flickr_data/users_unicode.txt', 'at', 'utf-8')
load_max_photos = 100
get_users_from_file(filename='flickr_data/FlickrUsernames.uniq.txt')
for path_alias in path_aliases:
    # person
    try:
        persons[path_alias] = flickr_api.Person.getByUrl('http://www.flickr.com/photos/%s' % path_alias)    #APICALL (n times)
        time.sleep(1)
        persons[path_alias].load()      #APICALL (n times)
        time.sleep(1)
    except:
        sys.stderr.write('Error with user %s\n' % path_alias)
        continue
    f.write(person_info(path_alias))
    f.write('\n')
f.close()