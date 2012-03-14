#!/usr/bin/env python

from xbmcswift import Plugin
from Downloader import extractSchools, Downloader, extractCollections,\
	extractSchoolCategories, extractExtras
import re
from urlparse import urlparse
from urllib import urlencode
from ParserLite3 import parseString, getSongName, getMediaURL,\
	getArtistName, getDuration, getFileExtension, getTrackNumber,\
	getReleaseDate, getDescription, getPlaylistName, getComposerName,\
	getCollectionCategory, getCategory, getArtworkURL
try:
	from urlparse import parse_qs
except ImportError:
	from cgi import parse_qs

__plugin_name__ = 'iTunesU'
__plugin_id__ = 'plugin.video.itunesu'
plugin = Plugin(__plugin_name__, __plugin_id__, __file__)

SCHOOL_LIST = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=%s"
VIEW_ITEM_BASE = "http://itunes.apple.com/WebObjects/DZR.woa/wa/downloadTracks?id=%d" #"http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=us&id=%d"
VIEW_ALL_COLLECTIONS = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewSeeAll?id=%d"
SCHOOL = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewArtist?id=%d"
VIEW_CATEGORY_COLLECTIONS = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewGenre?a=%d&id=%d"
VIEW_TAGGED_COLLECTIONS_TEMPLATE = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTagged?%s"

downloader = Downloader()

def noneIsEmpty(val):
	if val is None:
		return ''
	else:
		return val
	
def sortByLabel(items):
	return sorted(items, key=lambda x:x['label'])

def getQueryStringFromURL(url):
	parseResult = urlparse(url)
	
	if hasattr(parseResult, 'query'):
		return parseResult.query
	else:
		return parseResult[4]
	
def unescape(s):
	s = s.replace("&lt;", "<")
	s = s.replace("&gt;", ">")
	# this has to be last:
	s = s.replace("&amp;", "&")
	return s

def extractArtistId(url):
	url = unescape(url)
	regex = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewArtist\?id=(\d{9})"
	match = re.search(regex, url)
	if match:
		ret = str(match.group(1))
		return ret
	else:
		query = getQueryStringFromURL(url)
		values = parse_qs(query)
		id = values.get('id')
		if id:
			return id[0] # What happens if more?
		else:
			return None
	
def extractCollectionId(url):
	url = unescape(url)
	regex = "http://itunes.apple.com/us/itunes-u/[\w\-\.]*/id(\d{9})"
	match = re.search(regex, url)
	if match:
		ret = str(match.group(1))
		return ret
	else:
		query = getQueryStringFromURL(url)
		values = parse_qs(query)
		id = values.get('id')
		if id:
			return id[0] # What happens if more?
		else:
			return None
	
def extractCategoryId(url):
	url = unescape(url)
	regex = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewGenre\?a=\d{9}&id=(\d{8})"
	match = re.search(regex, url)
	if match:
		ret = str(match.group(1))
		return ret
	else:
		query = getQueryStringFromURL(url)
		values = parse_qs(query)
		id = values.get('id')
		if id:
			return id[0] # What happens if more?
		else:
			return None
	
def extractExtraId(url):
	url = unescape(url)
	query = getQueryStringFromURL(url) ## Also use regex?
	values = parse_qs(query)
	tag = values.get('tag')
	if tag:
		return tag[0] # What happens if more?
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

@plugin.cacheReturn()
def getAllSchools(schoolType):
	allSchoolsURL = SCHOOL_LIST % schoolType
	
	source = downloader.getSource2(url=allSchoolsURL)
	if source:
		ret = extractSchools(source)
	else:
		ret = {}
	
	return ret

@plugin.cacheReturn()
def getAllCollections(artistId):
	collections_url = VIEW_ALL_COLLECTIONS % artistId
	
	source = downloader.getSource2(url=collections_url)
	if source:
		ret = extractCollections(source)
	else:
		ret = {}
	
	return ret

@plugin.cacheReturn()
def getCategoryCollections(artistId, categoryId):
	collections_url = VIEW_CATEGORY_COLLECTIONS % (artistId, categoryId)
	
	source = downloader.getSource2(url=collections_url)
	if source:
		ret = extractCollections(source)
	else:
		ret = {}
	
	return ret

@plugin.cacheReturn()
def getTaggedCollections(artistId, tagName):
	params = {'tag':tagName, 'id':artistId}
	
	query = urlencode(params)
	
	collections_url = VIEW_TAGGED_COLLECTIONS_TEMPLATE % query
	
	source = downloader.getSource2(url=collections_url)
	if source:
		ret = extractCollections(source)
	else:
		ret = {}
	
	return ret

@plugin.cacheReturn()
def getSchoolPage(artistId):
	school_url = SCHOOL % artistId
	
	return downloader.getSource2(url=school_url)
	
def getExtras(artistId):
	source = getSchoolPage(artistId)
	if source:
		extras = extractExtras(source)
	else:
		extras = {}
	
	return extras


def getCategories(artistId):
	source = getSchoolPage(artistId)
	if source:
		cats = extractSchoolCategories(source)
	else:
		cats = {}
		
	return cats

@plugin.route('/schools/<schoolType>/')
def showSchoolList(schoolType):
	label_urls = getAllSchools(schoolType).iteritems()
	items = []
	for label, url in label_urls:
		artistId=extractArtistId(url)
		
		if artistId is None:
			print "Tossing school (no artistId): %s (%s)" % (schoolType, url)
			continue
				
		items.append(
					{
					'label': label, 
					'url': plugin.url_for('school', artistId=artistId), 
					}
		)
	
	return plugin.add_items(sortByLabel(items))

def getCategoryItems(categories, artistId):
	items = []
	for category, href in categories.iteritems():
		categoryId=extractCategoryId(href)
		
		if categoryId is None:
			print "Tossing category (no categoryId): %s (%s)" % (category, href)
			continue
		
		items += [
					{'label': category, 'url': plugin.url_for('categoryCollections', artistId=artistId, categoryId=categoryId)},
				 ]
	return items

def getExtraItems(categories, artistId):
	items = []
	for category, href in categories.iteritems():
		tagName=extractExtraId(href)
		
		if tagName is None:
			print "Tossing extra (no tagName): %s (%s)" % (category, href)
			continue
		
		items += [
				 	{'label': category, 'url': plugin.url_for('taggedCollections', artistId=artistId, tagName=tagName)},
				 ]
	return items

@plugin.route('/school/<artistId>/tagged/')
def taggedCollectionList(artistId):
	extras = getExtras(int(artistId))
	items = []
	for extra in extras:
		items += getExtraItems(extras[extra], artistId)
	
	return plugin.add_items(sortByLabel(items))

@plugin.route('/school/<artistId>/category/')
def categoryList(artistId):
	items = []
	
	categories = getCategories(int(artistId))
	items += getCategoryItems(categories, artistId)
	
	return plugin.add_items(sortByLabel(items))
		
@plugin.route('/school/<artistId>/')
def school(artistId):
	items = []
	
	items += [
		{'label': 'All Collections', 'url': plugin.url_for('allCollections', artistId=artistId)},
	]
	
	items += [
		{'label': 'Tagged Collections', 'url': plugin.url_for('taggedCollectionList', artistId=artistId)},
	]
	
	items += [
		{'label': 'Categories', 'url': plugin.url_for('categoryList', artistId=artistId)},
	]
	
	return plugin.add_items(items)

def renderCollections(collections):
	items = []
	for label, data in collections:
		href = data['href']
		collectionId = extractCollectionId(href)
		if collectionId is None:
			print "Tossing collection (no collectionId): %s" % (href)
			continue
		items.append(
					{
					'label': label, 
					'url': plugin.url_for('showCollection', collectionId=collectionId),
					'iconImage':noneIsEmpty(data.get('iconImage')), 
					'thumbnail': noneIsEmpty(data.get('thumbnail')),
					}
		)
	return plugin.add_items(sorted(items, key= lambda item: item['label']))

@plugin.route('/school/<artistId>/collections/')
def allCollections(artistId):
	collections = getAllCollections(int(artistId)).iteritems()  
	return renderCollections(collections)

@plugin.route('/school/<artistId>/category/<categoryId>')
def categoryCollections(artistId, categoryId):
	collections = getCategoryCollections(int(artistId), int(categoryId)).iteritems()  
	return renderCollections(collections)

@plugin.route('/school/<artistId>/tagged/<tagName>')
def taggedCollections(artistId, tagName):
	collections = getTaggedCollections(int(artistId), tagName).iteritems()  
	return renderCollections(collections)

def formatDuration(durationMS):
	seconds = durationMS / 1000
	
	hour = seconds / 3600
	seconds = seconds % 3600

	mins = seconds / 60
	
	return "%d:%02d" % (hour, mins)

@plugin.cacheReturn()
def getCollectionMediaItemsDicts(collectionId):
	url = VIEW_ITEM_BASE%(int(collectionId))
	return parseString(downloader.getSource2(url=url))
		
@plugin.route('/collection/<collectionId>/')
def showCollection(collectionId):
	mediaItemsDicts = getCollectionMediaItemsDicts(collectionId)
	
	items = []
	
	for mediaItem in mediaItemsDicts:
		
		title = getSongName(mediaItem)
		mediaURL = getMediaURL(mediaItem)
		author = getArtistName(mediaItem)
		durationMS = getDuration(mediaItem)
		extension = getFileExtension(mediaItem)
		trackNumber = getTrackNumber(mediaItem)
		releaseDate = getReleaseDate(mediaItem)
		description = getDescription(mediaItem)
		playlistName = getPlaylistName(mediaItem) 
		composerName = getComposerName(mediaItem)
		collectionCategory = getCollectionCategory(mediaItem)
		category = getCategory(mediaItem)
		iconImage = thumbnail = noneIsEmpty(getArtworkURL(mediaItem))
		
		tvshowtitle = "%s - %s" % (composerName, playlistName) # collectionTitle vs playlistName?
		if category != collectionCategory:
			genre = "%s - %s" % (collectionCategory, category)
		else:
			genre = collectionCategory
		
		date = releaseDate.strftime("%d.%m.%Y")
		premiered = releaseDate.strftime("%Y-%m-%d")
		year = releaseDate.year
		cast = [x.strip() for x in author.split(',')]
#		itemid = getItemId(mediaItem)
		
		if extension == 'mp4':
			overlay = 8
		else:
			overlay = 0
			
		duration = formatDuration(durationMS)
				
		items +=	[
					  {
					   'label': title,
					   'iconImage': iconImage, 
					   'thumbnail': thumbnail,
					   'url': mediaURL,
					   'is_playable': True,
					   'is_folder': False,
					   'info':{
#							'count': itemid,
							'plot': description, 
							'plotoutline': 'plotoutline', 
							'title': title,
							'tagline': 'tagline', 
							'genre': genre,
							'duration': duration, 
							'date': date,
							'episode': trackNumber,
							'overlay': overlay, 
							'year': year,
							'season': 1, ## XBMC seems to want some #
							'album':'album',
							'tvshowtitle': tvshowtitle,
#							'writer':None,
#							'director':None,
							'cast':cast,
							'premiered':premiered,
							'studio':composerName
						}
					   }
					]
	
	return plugin.add_items(items)  

if __name__ == '__main__': 
	plugin.run()
