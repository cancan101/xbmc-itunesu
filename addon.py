#!/usr/bin/env python

from xbmcswift import Plugin
from Downloader import extractSchools, Downloader, extractCollections
import re

__plugin_name__ = 'iTunesU'
__plugin_id__ = 'plugin.video.itunesu'
plugin = Plugin(__plugin_name__, __plugin_id__, __file__)

SCHOOL_LIST = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=%s"
VIEW_ITEM_BASE = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=us&id=%d"
VIEW_COLLECTIONS = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewSeeAll?id=%d"

downloader = Downloader()

def extractArtistId(url):
    regex = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewArtist\?id=(\d{9})"
    match = re.search(regex, url)
    if match:
        ret = str(match.group(1))
        return ret
    else:
        return None
    
def extractCollectionId(url):
    regex = "http://itunes.apple.com/us/itunes-u/[\w\-\.]*/id(\d{9})"
    match = re.search(regex, url)
    if match:
        ret = str(match.group(1))
        return ret
    else:
        return None

@plugin.route('/')
def show_homepage():
    items = [
        {'label': 'Universities & Colleges', 'url': plugin.url_for('showSchoolList', schoolType='EDU')},
        {'label': 'K-12', 'url': plugin.url_for('showSchoolList', schoolType='K12')},
        {'label': 'Beyond Campus', 'url': plugin.url_for('showSchoolList', schoolType='ORG')},
    ]
    return plugin.add_items(items)

def getAllSchools(schoolType):
    ret = downloader.gotoURL(url=SCHOOL_LIST%schoolType)
    if ret:
        source = ret.HTML
        ret = extractSchools(source)
    else:
        ret = {}
    
    return ret

def getAllCollections(artistId):
    collections_url = VIEW_COLLECTIONS % artistId
    
    ret = downloader.gotoURL(url=collections_url)
    if ret:
        source = ret.HTML
        ret = extractCollections(source)
    else:
        ret = {}
    
    return ret

@plugin.route('/schools/<schoolType>/')
def showSchoolList(schoolType):
    label_urls = getAllSchools(schoolType).iteritems()
            
    items = [{'label': label, 
        'url': plugin.url_for('school', artistId=extractArtistId(url)), 
        'is_playable': True, 
        'is_folder': False
        } for label, url in label_urls]
    return plugin.add_items(sorted(items, key= lambda item: item['label']))
    
@plugin.route('/school/<artistId>/')
def school(artistId):
    items = [
        {'label': 'Collections', 'url': plugin.url_for('collections', artistId=artistId)},
    ]
    return plugin.add_items(items)

@plugin.route('/school/<artistId>/collections/')
def collections(artistId):
    label_urls = getAllCollections(int(artistId)).iteritems()  
    
    items = [{'label': label, 
        'url': plugin.url_for('showCollection', collectionId=extractCollectionId(data['href'])), 
        'is_playable': True, 
        'is_folder': False
        } for label, data in label_urls]
    return plugin.add_items(sorted(items, key= lambda item: item['label']))

@plugin.route('/collection/<collectionId>/')
def showCollection(collectionId):
    items = [
        {'label': 'All Universities', 'url': plugin.url_for('showSchoolList', schoolType='EDU')},
    ]
    return plugin.add_items(items)  

if __name__ == '__main__': 
    plugin.run()
