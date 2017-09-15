__author__ = 'Jeremy'
import os
import xmltodict as xd

feedxml = "C:\Users\Jeremy\Google Drive\Code\Python Scripts\PlexCast\cnet-news.xml"

with open(feedxml) as fd:
    f = xd.parse(fd.read())

ch = f['rss']['channel']

feed = {
    "title":    ch['title'],
    "summary":  ch['description'],
    "xml":      feedxml
}

if 'itunes:author' in ch:
    feed['author'] = ch['itunes:author']

if 'itunes:summary' in ch:
    feed['summary'] = ch['itunes:summary']

if 'itunes:subtitle' in ch:
    feed['subtitle'] = ch['itunes:subtitle']

if 'itunes:image' in ch:
    feed['imgLarge'] = ch['itunes:image']['@href']

if 'image' in ch:
    feed['imgSmall'] = ch['image']['url']

if 'item' in ch:
    feed['episodes'] = []
    for i in ch['item']:
        ep = {
            'title'
        }

print feed
for i, j in feed.iteritems():
    print i
    print j


