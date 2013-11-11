import os
import sys
import datetime
import httplib
import time

sys.path.insert(0,"python-flickr-api")
import flickr_api       #APICALL (once)

photodir = '/home/henne/flickr/data/m'
donefile = 'checked_photos.csv'

newfiles = set()
donefiles = set()

def debug(str):
    print str

def readdone(donefile, donefiles):
    debug("readdone")
    try:
        f = open(donefile, 'rt')
        for line in f:
            donefiles.add(line.split(';')[0])
    except IOError:
        print 'if %s is not existing, please touch it' % donefile
        raise
    debug(" done: %s" % len(donefiles))

def readdir(newfiles, donefiles):
    debug("readdir")
    now = datetime.datetime.now()
    for f in os.listdir(photodir):
        if f not in donefiles:
            d = modification_date(os.path.join(photodir, f))
            #if (now - d > datetime.timedelta(days=17, hours=21, minutes=55)):
            if (now - d > datetime.timedelta(days=14)):
                newfiles.add(f)
    debug(" todo: %s" % len(newfiles))

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

def flickr_photo_gne(filename):
    conn = httplib.HTTPConnection('www.flickr.com')
    conn.request("GET", "/photo.gne?id=%s" % filename)
    r = conn.getresponse()
    if r.status == 302:
        if r.msg.dict['location'].find(filename) > -1:
            return "noauth", "noauth"
        url = r.msg.dict['location']
        trash, trash2, uid, pid, trash3 = url.split('/')
        return uid, pid
    elif r.status == 404:
        return "notex", "notex"
    print r.status, filename
    return r.status

def save(msg, newfiles, donefiles):
    f = open(donefile, 'at')
    f.write('%s\n' % msg)
    f.close()
    f = msg.split(';')[0]
    donefiles.add(f)
    #newfiles.remove(f)
    return None

def stats(newfiles, donefiles):
    if len(newfiles) % 10 == 0:
        debug("todo: %s, done: %s" % (len(newfiles), len(donefiles)))

def process(newfiles, donefiles):
    debug("process")
    while len(newfiles) > 0:
        f = newfiles.pop()
        stats(newfiles, donefiles)
        filepath = os.path.join(photodir, f)
        #d = modification_date(filepath)
        #now = datetime.datetime.now()
        #if (now - d > datetime.timedelta(days=14)):
        uid, pid = flickr_photo_gne(f)
        if uid == 'noauth':
            save("%s;access denied - login please" % f, newfiles, donefiles)
        elif uid == 'notex':
            save("%s;file not found" % f, newfiles, donefiles)
        try:
            p = flickr_api.Photo(id=pid)
            save("%s;OK" % f, newfiles, donefiles)
        except flickr_api.flickrerrors.FlickrAPIError as e:
            msg = e.__dict__['message']
            save("%s;%s" % (f, msg), newfiles, donefiles)
        time.sleep(3)
                


if __name__ == '__main__':
    while 42:
        readdone(donefile, donefiles)
        readdir(newfiles, donefiles)
        process(newfiles, donefiles)
        time.sleep(3600)

