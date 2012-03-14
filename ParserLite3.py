'''
Created on Mar 11, 2012

@author: alex
'''

from plistlib import readPlist, readPlistFromString, _dateFromString
import urlparse

def handleParsedDict(parsed):
	return parsed.get('collection')

def parseStream(stream):
	return handleParsedDict(readPlist(stream))

def parseString(string):
	return handleParsedDict(readPlistFromString(string))

#def makeTunesResults(mediaItems):
#	ret = []
#	for mediaItem in mediaItems:
#		title = getSongName(mediaItem)
#		previewurl = getMediaURL(mediaItem)
#		author = getArtistName(mediaItem)
#		duration = getDuration(mediaItem)
#		extension = getFileExtension(mediaItem)
#		itemid = getItemId(mediaItem)
#		ret.append(MediaItem(title, author, duration, extension, None, None, None, None, previewurl, None, itemid))
#	return ret


def getSongName(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("songName", metaData.get("itemName"))

def getArtistName(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("artistName")

def getDuration(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("duration")

def getComments(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("comments")

def getDescription(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("description") # "longDescription"

def getPlaylistName(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("playlistName")

def getMediaURL(mediaItem):
	return mediaItem.get("URL") # "previewURL", "episodeURL", "preview-url"

def getArtworkURL(mediaItem):
	return mediaItem.get("artworkURL")

def getReleaseDate(mediaItem):
	metaData = mediaItem.get('metadata', {})
	ret = metaData.get("releaseDate")
	if ret is not None:
		ret = _dateFromString(ret)
		
	return ret

def getModifyDate(mediaItem):
	metaData = mediaItem.get('metadata', {})
	ret = metaData.get("dateModified")
	if ret is not None:
		ret = _dateFromString(ret)
		
	return ret

def getItemId(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("episodeGUID", metaData.get("itemId"))

def getPathFromURL(url):
	parseResult = urlparse(url)
	
	if hasattr(parseResult, 'path'):
		return parseResult.query
	else:
		return parseResult[2]

def getFileExtension(mediaItem):	
	metaData = mediaItem.get('metadata', {})
#	url = getMediaURL(mediaItem)
#	TODO: use getMediaURL + getPathFromURL + path splitting to get extension
	return metaData.get("fileExtension")

def getTrackNumber(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("trackNumber")	

def getComposerName(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("composerName")

def getCategory(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("category")

def getCollectionCategory(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("collectionCategory")

def getCollectionTitle(mediaItem):
	metaData = mediaItem.get('metadata', {})
	return metaData.get("collectionTitle")	
	
#print makeTunesResults(parseStream(open('download.xml')))