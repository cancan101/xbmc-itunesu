import ParserBase

class MediaItem(object):
    def __init__(self, title, author, duration, type, comment, releasedate,
            datemodified, gotourl, previewurl, price, itemid):
        
        self.title=title
        self.author=author
        self.gotourl=gotourl
        self.duration=duration
        self.type=type
        self.comment=comment
        self.releasedate=releasedate
        self.datemodified=datemodified
        self.previewurl=previewurl
        self.price=price
        self.itemid=itemid

class Parser(ParserBase.ParserBase):
    def addItem(self, title, author, duration, type, comment, releasedate,
            datemodified, gotourl, previewurl, price, itemid):
        """Adds item to media list."""
        item = MediaItem(title, author, duration, type, comment, releasedate, datemodified, gotourl, previewurl, price, itemid)
        
        self.addItemHelper(item)