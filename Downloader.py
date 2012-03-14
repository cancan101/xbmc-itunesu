'''
Created on Feb 21, 2012

@author: alex
'''
from TunesViewerBase import TunesViewerBase
from constant_constants import USER_AGENT
import gzip
try:
	import cStringIO as StringIO
except ImportError:
	import StringIO
import logging
from BeautifulSoup import BeautifulSoup as BS

def htmlentitydecode(s):
	if s:
		# This unescape function is an internal function of
		# HTMLParser but let's use it, as it does a better job than
		# what we have so far.
		#
		# See: hg.python.org/cpython/file/2.7/Lib/HTMLParser.py
		import HTMLParser
		return HTMLParser.HTMLParser().unescape(s).replace("&apos;", "'")
	else:
		return ""

class Downloader( TunesViewerBase ):
	def __init__(self):
		super(Downloader, self).__init__(USER_AGENT)
		
	def loadPage(self, url):
		text = None
		try:
			response = self.opener.open(url)
			response_info = response.info()
			pageType = response_info.getheader('Content-Type', 'noheader?')
#			logging.debug("pageType = %s" % (pageType))
			if pageType.startswith("text"):
				text = response.read()
				if response_info.get('Content-Encoding') == 'gzip':
					orig = len(text)
					f = gzip.GzipFile(fileobj=StringIO.StringIO(text))
					try:
						text = f.read()
						logging.debug("Gzipped response: " + str(orig) + "->" + str(len(text)))
					except IOError, e: #bad file
						logging.debug(str(e))
						return None
			else:
				print "Not text"
				return None
			response.close()
		except Exception, e:
			logging.error(e)
			return None
		
		return text
						
	def getSource2(self, url):
		return self.loadPage(url=url)

def extractSchools(source):
	soup = BS(source)
	parent_div = soup.find('div', "grouping-text-content")
	schools_li = parent_div.findAll('li')

	schools_a = [s.find("a") for s in schools_li]
	ret = {}
	for school in schools_a:
		if school is None:
			logging.debug("Tossing school")
			continue
		else:
			title = school.get("title")
			href = school.get("href")
			ret[title] = href
	
	return ret

def extractTitledbox(parent_div):
	categories_li = parent_div.findAll('li')
	categories_a = [s.find("a") for s in categories_li]
	
	ret = {}
	for category_a in categories_a:
		category = htmlentitydecode(category_a.text)
		href = category_a.get("href")
		ret[category] = href
		
	return ret	

def extractSchoolCategories(source):
	soup = BS(source)
	parent_div = soup.find('div', {'class':'extra-list', 'metrics-loc':'Titledbox_Categories'})
	
	return extractTitledbox(parent_div)

	
def extractCollections(source):
	soup = BS(source)
	collections_div = soup.findAll('div', "lockup small detailed option podcast video")
	
	ret = {}
	for collection_div in collections_div:
		collection = collection_div.find("ul", "list").find('li', 'name').find('a')
		if collection is None:
			logging.debug("Tossing Collection")
			continue
		else:
			artwork_div = collection_div.find("div", "artwork")
			thumbnail = None
			iconImage = None
			if artwork_div is not None:
				artwork = artwork_div.find('img', 'artwork src-swap')
				if artwork is not None:
					artworkImage = str(artwork.get('src-swap'))
					thumbnail = artworkImage.replace('.75x75-65', '')
					iconImage = thumbnail ### http://forum.xbmc.org/showthread.php?p=53916
					
			title = title_orig = htmlentitydecode(collection.text)
			href = collection.get("href")
			count = 0
			while title in ret:
				count+=1
				title = "%s alt%d" % (title_orig, count)
			ret[title] = {'href':href, 'thumbnail':thumbnail, 'iconImage':iconImage}
	
	return ret

def extractExtras(source):
	soup = BS(source)
	top_div = soup.find('div', {'class':'extra-list', 'metrics-loc':'Titledbox_Top Collections'})
	extras = top_div.findNextSiblings('div', 'extra-list')
	
	ret = {}
	for extra in extras:
		extra_title = extra.get('metrics-loc').replace('Titledbox_', '')
		ret[extra_title] = extractTitledbox(extra)
	
	return ret 