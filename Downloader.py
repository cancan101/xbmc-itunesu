'''
Created on Feb 21, 2012

@author: alex
'''
from TunesViewerBase import TunesViewerBase
from constant_constants import USER_AGENT
import gzip
from StringIO import StringIO
import logging
from ParserSimple import Parser
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from common import htmlentitydecode

class Downloader( TunesViewerBase ):
    def __init__(self):
        super(Downloader, self).__init__(USER_AGENT)
        
    def loadPage(self, url):
        text = None
        try:
            response = self.opener.open(url)
            response_info = response.info()
            pageType = response_info.getheader('Content-Type', 'noheader?')
#            logging.debug("pageType = %s" % (pageType))
            if pageType.startswith("text"):
                text = response.read()
                if response_info.get('Content-Encoding') == 'gzip':
                    orig = len(text)
                    f = gzip.GzipFile(fileobj=StringIO(text))
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
    
    def processPage(self, url, source):
        #Parse the page and display:
        logging.debug("PARSING " + url)
        parser = Parser(url, contentType=None, source=source)
        if parser.Redirect != "":
            logging.debug("REDIRECT: " + parser.Redirect)
            self.gotoURL(parser.Redirect)
        elif len(parser.mediaItems) == 1 and parser.singleItem:
            print "Single item description page."
            #Single item description page.
#            self.startDownload(parser.mediaItems[0])
            return parser
        else: #normal page
            logging.debug("normal page: %s" % url)
            logging.debug("Title: %s" % parser.Title)
            logging.debug("ITEMS: " + str(len(parser.mediaItems)))
#            logging.debug(parser.HTML)
            for i in range(len(parser.tabMatches)):
                logging.debug("Tab %s %s" % (parser.tabMatches[i], parser.tabLinks[i]))
            return parser
                
    def gotoURL(self, url):
        source = self.loadPage(url=url)
        if source:
            return self.processPage(url, source)
        else:
            return None                 

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

def extractSchoolCategories(source):
    soup = BS(source)
    parent_div = soup.find('div', {'class':'extra-list', 'metrics-loc':'Titledbox_Categories'})    
    categories_li = parent_div.findAll('li')
    categories_a = [s.find("a") for s in categories_li]
    
    ret = {}
    for category_a in categories_a:
        category = htmlentitydecode(category_a.text)
        href = category_a.get("href")
        ret[category] = href
        
    return ret
    
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
                    iconImage = str(artwork.get('src-swap'))
                    thumbnail = iconImage.replace('.75x75-65', '')
              
            title = title_orig = htmlentitydecode(collection.text)
            href = collection.get("href")
            count = 0
            while title in ret:
                count+=1
                title = "%s alt%d" % (title_orig, count)
            ret[title] = {'href':href, 'thumbnail':thumbnail, 'iconImage':iconImage}
    
    return ret

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewArtist?id=341593265"#"http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=379060688"#"http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=us&id=354868877"#"http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTagged?tag=MIT+OpenCourseWare&id=341593265"
    dl = Downloader()
    ret = dl.gotoURL(url)
    if ret:
        source = ret.HTML
        print extractSchoolCategories(source)
#        print extractCollections(source)
#        print extractSchools(source)


       

    #All Universities:    http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=EDU
    #Uni USA:             http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=EDU&mzcc=US
    #K12                  http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=K12
    #K12 USA              http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=K12&mzcc=US
    
    #Social Science by release date:
    # 1-180: http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=432944739&genreIdString=40000094&mediaTypeString=iTunes+U
    
    # Example of Redirect:
    # http://itunes.apple.com/us/institution/mit/id341593265
    # ---> http://itunes.apple.com/WebObjects/DZR.woa/wa/viewArtist?cc=us&id=341593265
    
    # Videos (same destination): 
    #        http://deimos3.apple.com/WebObjects/Core.woa/Browse/mit.edu.2275469498.02275469503.2275329397?i=1656542916
    #        http://deimos3.apple.com/WebObjects/Core.woa/Browse/mit.edu.2275469498.02275469503.2275902819?i=1165575714

    # Video file:
    # http://deimos3.apple.com/WebObjects/Core.woa/DownloadTrackPreview/mit.edu-dz.3304655185.03304655187.3304655213/enclosure.mp4