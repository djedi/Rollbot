import sys
import re
import urllib

import BeautifulSoup
from HTMLParser import HTMLParseError

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

class MyBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def signedOn(self):
        self.join(self.factory.channel)
        print "Signed on as %s." % (self.nickname)

    def joined(self, channel):
        print "Joined %s." % channel

    def privmsg(self, user, channel, msg):
        # get title of urls
        matches = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        if matches:
            for url in matches:
                u = urllib.urlopen(url)
                urltype = u.headers.gettype()
                print urltype
                try:
                    soup = BeautifulSoup.BeautifulSoup(u)
                    title = re.sub("\s+", ' ', soup.title.string).strip()
                    self.msg(self.factory.channel, "Title: %s" % str(title))
                except (AttributeError, HTMLParseError):
                    u = urllib.urlopen(url)
                    self.msg(self.factory.channel, \
                        "NO TITLE FOUND (%s)" % urltype)

class MyBotFactory(protocol.ClientFactory):
    protocol = MyBot

    def __init__(self, channel, nickname="Rollbot"):
        self.channel = channel
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % reason

if __name__ == "__main__":
    try:
        chan = sys.argv[1]
        reactor.connectTCP('irc.freenode.net', 6667, MyBotFactory('#' + chan))
        reactor.run()
    except IndexError:
        print "Please specify a channel name."
        print "Example:"
        print "    python %s somechannel" % sys.argv[0]
