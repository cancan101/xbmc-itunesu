'''
Created on Feb 20, 2012

@author: alex
'''
import cookielib
import urllib2
import time

class TunesViewerBase( object ):
    def __init__(self, ua):
        self.ua = ua
        
        # Set up the main url handler with downloading and cookies:
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self.opener.addheaders = [('User-agent', ua),
                      ('Accept-Encoding', 'gzip'),
                      ('Accept-Language', 'en-US')]
        
    def setHeaders(self, htmMode, mobileMode):
        #Apparently the x-apple-tz header is UTC offset *60 *60.
        tz = str(-time.altzone)
        self.opener.addheaders = [('User-agent', self.ua),
                      ('Accept-Encoding', 'gzip'),
                      ('X-Apple-Tz', tz)]
       
        if htmMode:
            self.opener.addheaders = [('User-agent', self.ua),
                          ('Accept-Encoding', 'gzip'),
                          ("X-Apple-Tz:", tz),
                          ("X-Apple-Store-Front", "143441-1,12")]
        if mobileMode:
            # As described on
            # http://blogs.oreilly.com/iphone/2008/03/tmi-apples-appstore-protocol-g.html
            self.opener.addheaders = [('User-agent', 'iTunes-iPhone/1.2.0'),
                          ('Accept-Encoding', 'gzip'),
                          ('X-Apple-Store-Front:', '143441-1,2')]