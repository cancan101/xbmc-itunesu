#!/usr/bin/env python

from xbmcswift import Plugin
from Downloader import extractSchools, Downloader, extractCollections,\
    extractSchoolCategories
import re

__plugin_name__ = 'iTunesU'
__plugin_id__ = 'plugin.video.itunesu'
plugin = Plugin(__plugin_name__, __plugin_id__, __file__)

SCHOOL_LIST = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=%s"
VIEW_ITEM_BASE = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=us&id=%d"
VIEW_ALL_COLLECTIONS = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewSeeAll?id=%d"
SCHOOL = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewArtist?id=%d"
VIEW_CATEGORY_COLLECTIONS = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewGenre?a=%d&id=%d"

downloader = Downloader()

def noneIsEmpty(val):
    if val is None:
        return ''
    else:
        return val

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
    
def extractCategoryId(url):
    regex = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewGenre\?a=\d{9}&id=(\d{8})"
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
    collections_url = VIEW_ALL_COLLECTIONS % artistId
    
    ret = downloader.gotoURL(url=collections_url)
    if ret:
        source = ret.HTML
        ret = extractCollections(source)
    else:
        ret = {}
    
    return ret

def getCategoryCollections(artistId, categoryId):
    collections_url = VIEW_CATEGORY_COLLECTIONS % (artistId, categoryId)
    
    ret = downloader.gotoURL(url=collections_url)
    if ret:
        source = ret.HTML
        ret = extractCollections(source)
    else:
        ret = {}
    
    return ret

def getAllCategories(artistId):
    categories_url = SCHOOL % artistId
    
    ret = downloader.gotoURL(url=categories_url)
    if ret:
        source = ret.HTML
        ret = extractSchoolCategories(source)
    else:
        ret = {}
    
    return ret

@plugin.route('/schools/<schoolType>/')
def showSchoolList(schoolType):
    label_urls = getAllSchools(schoolType).iteritems()
            
    items = [{'label': label, 
        'url': plugin.url_for('school', artistId=extractArtistId(url)), 
        } for label, url in label_urls]
    return plugin.add_items(sorted(items, key= lambda item: item['label']))
    
@plugin.route('/school/<artistId>/')
def school(artistId):
    items = [
        {'label': 'All Collections', 'url': plugin.url_for('allCollections', artistId=artistId)},
    ]
    categories = getAllCategories(int(artistId))

    for category, href in categories.iteritems():
        categoryId=extractCategoryId(href)
        
        if categoryId is None:
            print "Tossing category (no categoryId): %s (%s)" % (category, href)
            continue
        
        items += [
                  {'label': category, 'url': plugin.url_for('categoryCollections', artistId=artistId, categoryId=categoryId)},
                  ]

    return plugin.add_items(items)

def renderCollections(collections):
    items = [{
        'label': label, 
        'url': plugin.url_for('showCollection', collectionId=extractCollectionId(data['href'])),
        'iconImage':noneIsEmpty(data.get('iconImage')), 
        'thumbnail': noneIsEmpty(data.get('thumbnail')),
        } for label, data in collections]
    return plugin.add_items(sorted(items, key= lambda item: item['label']))

@plugin.route('/school/<artistId>/collections/')
def allCollections(artistId):
    collections = getAllCollections(int(artistId)).iteritems()  
    return renderCollections(collections)

@plugin.route('/school/<artistId>/category/<categoryId>')
def categoryCollections(artistId, categoryId):
    collections = getCategoryCollections(int(artistId), int(categoryId)).iteritems()  
    return renderCollections(collections)


@plugin.route('/collection/<collectionId>/')
def showCollection(collectionId):
    url = VIEW_ITEM_BASE%(int(collectionId))
    ret = downloader.gotoURL(url=url)
    
    items = []
    
    for mediaItem in ret.mediaItems:
        items +=    [
                      {'label': mediaItem.title,
                       'url': mediaItem.previewurl,
                        'is_playable': True,
                        'is_folder': False,
                        }
                    ]
    
    return plugin.add_items(items)  

if __name__ == '__main__': 
    plugin.run()
