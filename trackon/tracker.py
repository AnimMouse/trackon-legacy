from hashlib import md5
from time import time
from google.appengine.api.urlfetch import fetch, Error as FetchError, DownloadError
from google.appengine.api import memcache as MC
from google.appengine.api import datastore as DS
from google.appengine.api.labs import taskqueue as TQ
from trackon.bencode import bdecode

update_queue = TQ.Queue('update-trackers')
incoming_queue = TQ.Queue('new-trackers')

def trackerhash(addr):
    """Generate a 'fake' info_hash to be used with this tracker."""
    return md5(addr).hexdigest()[:20]

def genqstr(h):
    peerid = "-TO0001-XX"+str(int(time())) # 'random' peer id
    return "?info_hash=%s&port=999&peer_id=%s" % (h, peerid)

def check(addr):
    """Check if a tracker is up."""
    thash = trackerhash(addr) # The info_hash we will use for this tracker 
    requrl = addr+genqstr(thash)
    d = {}
    try:
        t1 = time()
        r = fetch(requrl, deadline=10)
        d['latency'] = time() - t1
    except DownloadError, e:
        d['error'] = "Could not reach tracker." # XXX Should find out why!
    except FetchError, e:
        d['error'] = "Fetchurl error: %s" % repr(e)
    
    if 'error' in d:
        d['latency'] = time() - t1
        return (d, requrl)


    if r.status_code != 200:
        d['error'] = "Unexpected HTTP status: %d" % r.status_code
    
    elif not r.content:
        d['error'] = "Got empty HTTP response."

    else:
        try:
            d['response'] = bdecode(r.content)
        except:
            d['error'] = "Couldn't bdecode response: %s." % r.content

    if 'response' in d:
        if 'failure reason' in d['response']:
            d['error'] = "Tracker failure reason: %s." % d['response']['failure reason']
        elif 'peers' not in d['response']:
            d['error'] = "Invalid response, 'peers' field is missing!"

    # TODO Do a more extensive check of what was returned

    return (d, requrl) 


def update(t, info):
    tim = int(time())
    info['updated'] = tim
    MC.set(t, info, namespace="status")

    # Status log 
    MC.set("%s!%d" % (t, tim), info, namespace="logs")
    l = MC.get(t, namespace="logs") or []
    l.insert(0, tim)
    MC.set(t, l[:64], namespace="logs") # Keep 64 samples

def add(t, info):
    l = MC.get('tracker-list') or []
    l.append(t) # XXX Rare race, we avoid it by having a single task in bucket.
    MC.set('tracker-list', l)

    update(t, info)
    debug("Added tracker: %s"%t)

def incoming(t):
    """Add a tracker to the list of trackers to check before adding to the proper tracker list"""
    task = TQ.Task(params={'tracker-address': t, 'attempts': 0})
    incoming_queue.add(task)

def allinfo():
    tl = MC.get('tracker-list')
    ts = {}
    if tl:
        ts = MC.get_multi(tl, namespace='status')

    return ts
