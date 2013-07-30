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
        self.join(self.factory.channel, self.factory.password)
        print "Signed on as {}".format(self.nickname)

    def joined(self, channel):
        print "Joined %s." % channel

    def privmsg(self, user, channel, msg):
        # get title of urls
        matches = re.findall(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
            r'(?:%[0-9a-fA-F][0-9a-fA-F]))+', msg)
        if matches:
            for url in matches:
                u = urllib.urlopen(url)
                urltype = u.headers.gettype()
                print urltype
                try:
                    soup = BeautifulSoup.BeautifulSoup(u)
                    title = re.sub("\s+", ' ', soup.title.string).strip()
                    title = title.encode('ascii', 'ignore')
                    self.msg(self.factory.channel, "Title: %s" % str(title))
                except (AttributeError, HTMLParseError):
                    urllib.urlopen(url)
                    self.msg(self.factory.channel,
                             "NO TITLE FOUND (%s)" % urltype)


class MyBotFactory(protocol.ClientFactory):
    protocol = MyBot

    def __init__(self, channel, nickname="Rollbot", password=None):
        self.channel = '#{}'.format(channel)
        self.nickname = nickname
        self.password = password

    def clientConnectionLost(self, connector, reason):
        print "Lost connection (%s), reconnecting." % reason
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect: %s" % reason

if __name__ == "__main__":
    try:
        channel = sys.argv[1]
        password = None
        if len(sys.argv) == 3:
            password = sys.argv[2]
        reactor.connectTCP('irc.freenode.net', 6667, MyBotFactory(
            channel=channel, password=password))
        reactor.run()
    except IndexError:
        print "Please specify a channel name."
        print "Example:"
        print "    python %s somechannel [channel_password]" % sys.argv[0]
