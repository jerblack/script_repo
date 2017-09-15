__author__ = 'Jeremy'
from plexapi.server import PlexServer
uri = 'http://192.168.0.5:32400'
p = PlexServer(baseuri=uri)
print p.library.section("Jeremy's TV").__dict__
# {'scanner': 'Plex Series Scanner',
#  'language': 'en',
#  'title': "Jeremy's TV",
#  'server': <PlexServer:http://192.168.0.5:32400>,
#  'initpath': '/library/sections',
#  'key': '9',
#  'type': 'show'}
print dir(p.library.section("Jeremy's TV"))
 # 'all', 'analyze', 'contentRating',
#  'emptyTrash', 'firstCharacter', 'genre', 'get', 'initpath',
#  'key', 'language', 'newest', 'onDeck', 'recentlyAdded', 'recentlyViewed',
#  'recentlyViewedShows', 'refresh', 'scanner', 'search', 'searchEpisodes',
#  'server', 'title', 'type', 'unwatched', 'year']
print dir(p.library.section("Jeremy's TV").get('Helix'))
# {'rating': '7.9', 'art': '/library/metadata/1840/art/1431536413',
#  'addedAt': datetime.datetime(2015, 4, 10, 21, 11, 23),
#  'updatedAt': datetime.datetime(2015, 5, 13, 10, 0, 13),
#  'ratingKey': '1840', 'player': None, 'year': 2014,
#  'duration': 3600000,
#  'originallyAvailableAt': datetime.datetime(2014, 1, 10, 0, 0),
#  'lastViewedAt': datetime.datetime(2015, 7, 29, 2, 40, 13),
#  'thumb': '/library/metadata/1840/thumb/1431536413',
#  'title': 'Helix', 'leafCount': 10, 'contentRating': 'TV-14',
#  'theme': '/library/metadata/1840/theme/1431536413',
#  'type': 'show', 'childCount': 1, 'viewedLeafCount': 2,
#  'studio': 'Syfy', 'user': None,
#  'key': '/library/metadata/1840/children',
#  'banner': '/library/metadata/1840/banner/1431536413',
#  'summary': "A team of scientists from the Centre for Disease Control "
#             "travel to a high tech research facility in the Arctic to"
#             " investigate a possible disease outbreak, only to find"
#             " themselves pulled into a terrifying life-and-death struggle "
#             "that holds the key to mankind's salvation...or "
#             "total annihilation.",
#  'server': <PlexServer:http://192.168.0.5:32400>,
#     'initpath': '/library/sections/9/all'}

['TYPE', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__',
 '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__',
 '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
 '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
 '_find_player', '_find_user', '_loadData', 'addedAt', 'analyze', 'art',
 'banner', 'childCount', 'contentRating', 'duration', 'episode', 'episodes',
 'get', 'getStreamUrl', 'initpath', 'isFullObject', 'isPartialObject',
 'iter_parts', 'key', 'lastViewedAt', 'leafCount', 'markUnwatched',
 'markWatched', 'originallyAvailableAt', 'play', 'player', 'rating',
 'ratingKey', 'refresh', 'reload', 'season', 'seasons', 'server', 'studio',
 'summary', 'theme', 'thumb', 'thumbUrl', 'title', 'type', 'unwatched',
 'updatedAt', 'user', 'viewedLeafCount', 'watched', 'year']

print p.library.section("Jeremy's TV").get('Helix').episodes()[2].getStreamUrl()
# 0 for unwatched, 1 for watched
['__add__', '__class__', '__contains__', '__delattr__', '__delitem__',
 '__delslice__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__',
 '__getitem__', '__getslice__', '__gt__', '__hash__', '__iadd__', '__imul__',
 '__init__', '__iter__', '__le__', '__len__', '__lt__', '__mul__', '__ne__',
 '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__reversed__',
 '__rmul__', '__setattr__', '__setitem__', '__setslice__', '__sizeof__',
 '__str__', '__subclasshook__', 'append', 'count', 'extend', 'index', 'insert',
 'pop', 'remove', 'reverse', 'sort']

['TYPE', '__class__', '__delattr__', '__dict__', '__doc__', '__eq__',
 '__format__', '__getattr__', '__getattribute__', '__hash__', '__init__',
 '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
 '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__',
 '_find_player', '_find_user', '_loadData', 'addedAt', 'analyze',
 'contentRating', 'duration', 'getStreamUrl', 'grandparentTitle',
 'index', 'initpath', 'isFullObject', 'isPartialObject', 'iter_parts',
 'key', 'lastViewedAt', 'markUnwatched', 'markWatched',
 'originallyAvailableAt', 'parentIndex', 'parentKey', 'parentThumb',
 'play', 'player', 'rating', 'ratingKey', 'refresh', 'reload', 'season',
 'server', 'show', 'summary', 'thumb', 'thumbUrl', 'title', 'type',
 'updatedAt', 'user', 'viewCount', 'viewOffset', 'year']


h = p.library.section("Jeremy's TV").get('Helix')
print h
