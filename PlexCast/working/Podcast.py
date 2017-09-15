__author__ = 'Jeremy'
from Queue import Queue
import os, podcastparser, urllib2, random, time, pprint, requests, threading, logging
import xml.etree.ElementTree as ET
import sqlite3 as sql


class Config:
    library_path = 'D:\\PlexCast'
    temp_path = os.path.join(library_path, "temp")
    db = os.path.join(library_path, 'plexcast.db')
    log_file = os.path.join(library_path, 'plexcast.log')
    default_feed = "http://feed.cnet.com/feed/podcast/cnet-news/hd.xml"
    feed2 = 'http://podcastfeeds.nbcnews.com/audio/podcast/MSNBC-MADDOW-NETCAST-M4V.xml'
    default_ep = 'http://dw.cbsi.com/redir/E32015_SonyPS_573519_2696.mp4?destUrl=http://download.cnettv.com.edgesuite.net/21923/mpx/2015/06/16/465136195960/E32015_SonyPS_573519_2696.mp4'
    dl_ext = ".downloading"
    accepted_extensions = ["mp4", "m4v", "mov", "avi", "wmv", "jpg", "png"]
    download_types = ['show_image', 'ep_video', 'ep_image']

    ep_db_checked = False
    show_db_checked = False
    download_threads = 3
    default_del_watched = True
    default_order = "new_first"  # new_first, old_first
    default_num_eps = 2
    count_kept_eps_in_num_eps = False

    def __init__(self):
        pass


def main():
    p1 = PodcastFeed(Config.default_feed)
    # p1.add_show()
    # p1.write_metadata()

    p2 = PodcastFeed(Config.feed2)
    # p2.add_show()
    # p2.write_metadata()
    # e = Episode.from_db(Config.default_ep)
    # e.write_metadata()
    # e.move()
    # e.download()
    for e in p1.episodes:
        e.write_metadata()

    # d = Download(e)
    # d.download(1)
    # print e.date
    # print Utils.get_time(e.date)
    # print Utils.get_time_tuple(e.date)


class Show:
    statuses = ["new", "active", "paused"]
    def __init__(self, show_url):
        self.info, self.name, self.show_page, self.description = '', '', '', ''
        self.image, self.id, self.date_added, self.base_path = '', '', '', ''
        self.episodes = []
        self.files = {}  # 'image', 'nfo'
        self.show_url = show_url
        self.status = self.statuses[0]  # new, active, paused, delete
        self.num_eps = Config.default_num_eps
        self.del_watched = Config.default_del_watched
        self.order = Config.default_order
        self.type = ''
        self.ep_count = 0
        self.in_db = False
        self.check_db_for_show()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __str__(self):
        return str(self.__dict__)

    @classmethod
    def from_db_by_id(cls, show_id):
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        ex_string = 'SELECT show_url FROM shows WHERE id = "' + show_id + '"'
        c.execute(ex_string)
        shows = c.fetchall()
        conn.commit()
        conn.close()
        if shows.__len__() > 0:
            return cls(shows[0][0])

    def download_image(self):
        d = Download('show', self.image)
        downloaded_file = d.download()
        if not downloaded_file:
            log.error('Show image failed to download: ' + self.image)
            return False
        else:
            src_loc = os.path.join(Config.temp_path, downloaded_file)
            dst_loc = os.path.join(self.base_path, downloaded_file)
            if os.path.exists(dst_loc):
                os.remove(dst_loc)
            os.rename(src_loc, dst_loc)
            self.files['image'] = dst_loc
            self.update_db()
            log('Show image downloaded: %s' % downloaded_file)
            return True

    def write_metadata(self):
        nfo_name = os.path.join(self.base_path, 'tvshow.nfo')
        header = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>'
        tv_show = ET.Element('tvshow')
        show_fields = {
            #----Used by agent---------#
            'title': self.name,
            'showtitle': self.name,
            'year': '0',
            'season': '-1',
            'plot': self.description,
            'playcount': '0',
            'id': self.id,
            'genre': self.type,
            'premiered': self.date_added,
            'status': self.status,
            'aired': self.date_added,
            'studio': self.name,
            'dateadded': self.date_added,
            #----Extra-----------------#
            'num_eps': str(self.num_eps),
            'ep_count': str(self.ep_count),
            'del_watched': str(self.del_watched),
            'order': self.order,
            'show_page': self.show_page,
            'show_url': self.show_url,
            'base_path': self.base_path
        }

        for f in show_fields:
            x = ET.SubElement(tv_show, f)
            x.text = show_fields[f]

        output_file = open(nfo_name, 'w')
        output_file.write(header)
        output_file.write(ET.tostring(tv_show))
        output_file.close()
        self.files['nfo'] = nfo_name
        self.update_db()

    def add_show(self):
        self.status = "active"
        self.add_to_db()
        for e in self.episodes:
            e.add_to_db()
        self.create_path()
        self.write_metadata()
        self.download_image()

    def delete(self, eps_too):
        self.status = 'delete'
        pass

    def pause(self):
        pass

    def print_show(self):
        pprint.pprint(self.__dict__)
        for e in self.episodes:
            pprint.pprint(e.__dict__)

    def create_path(self):
        p = os.path.join(Config.library_path, self.name)
        if not (os.path.exists(p)):
            os.mkdir(p)
        self.base_path = p

    def add_to_db(self):
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        # print 'data added is '+self.date_added

        c.execute('SELECT * FROM shows WHERE show_url = "' + self.show_url + '"')
        shows = c.fetchall()
        if shows.__len__() == 0:
            c.execute("INSERT INTO shows VALUES(?, ?, ?, ?, ?, ?, ?, ?, date('now'), ?, ?, ?, ?, ?, ?);",
                      (self.name, self.show_url, self.show_page, self.description,
                       self.image, self.id, self.base_path, self.status,
                       repr(self.files), self.type, self.order, self.del_watched, self.num_eps, self.ep_count))
            conn.commit()
            conn.close()
            self.in_db = True
            return 0
        else:
            self.id = shows[0][5]
            return 1

    def update_db(self): # use after changing fields
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute("UPDATE shows SET name=? WHERE id = ?",(self.name, self.id))
        c.execute("UPDATE shows SET show_url=? WHERE id = ?", (self.show_url, self.id))
        c.execute("UPDATE shows SET show_page=? WHERE id = ?", (self.show_page, self.id))
        c.execute("UPDATE shows SET description=? WHERE id = ?", (self.description, self.id))
        c.execute("UPDATE shows SET image=? WHERE id = ?", (self.image, self.id))
        c.execute("UPDATE shows SET base_path=? WHERE id = ?", (self.base_path, self.id))
        c.execute("UPDATE shows SET status=? WHERE id = ?", (self.status, self.id))
        c.execute("UPDATE shows SET files=? WHERE id = ?", (repr(self.files), self.id))
        c.execute("UPDATE shows SET ep_order=? WHERE id = ?", (self.order, self.id))
        c.execute("UPDATE shows SET del_watched=? WHERE id = ?", (self.del_watched, self.id))
        c.execute("UPDATE shows SET num_eps=? WHERE id = ?", (self.num_eps, self.id))
        c.execute("UPDATE shows SET ep_count=? WHERE id = ?", (self.ep_count, self.id))
        conn.commit()
        conn.close()

    def check_db_for_show(self):
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute('SELECT * FROM shows WHERE show_url = "' + self.show_url + '"')
        shows = c.fetchall()
        conn.commit()
        conn.close()
        if shows.__len__() > 0:
            s = shows[0]
            self.name = s[0]
            self.show_page = s[2]
            self.description = s[3]
            self.image = s[4]
            self.id = s[5]
            self.base_path = s[6]
            self.status = s[7]
            self.date_added = s[8]
            self.files = eval(s[9])
            self.type = s[10]
            self.order = s[11]
            self.del_watched = s[12]
            self.num_eps = s[13]
            self.ep_count = s[14]
            self.in_db = True
            self.all_eps_from_db()

    def all_eps_from_db(self):
        Episode.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute('SELECT * FROM episodes WHERE id  = ' + self.id)
        r = c.fetchall()
        for e in r:
            ep = Episode(e[0], e[1], e[2], e[3], e[4], self)
            if ep not in self.episodes:
                self.episodes.append(ep)

    def update_from_url(self):
        raise NotImplementedError

    @staticmethod
    def update_all():
        conn = sql.connect(Config.db)
        c = conn.cursor()
        ex_string = 'SELECT * FROM shows WHERE status = "active"'
        c.execute(ex_string)
        shows = c.fetchall()
        conn.commit()
        conn.close()
        for s in shows:
            if s[10] == "podcast":
                sh = PodcastFeed(s[1])
            elif s[10] == "youtube_channel":
                sh = YouTubeChannel(s[1])
            sh.update_from_url()

    @staticmethod
    def verify_db():
        if not Config.show_db_checked:
            conn = sql.connect(Config.db)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS shows(name TEXT' +
                      ', show_url TEXT, show_page TEXT, description TEXT, image TEXT' +
                      ', id TEXT, base_path TEXT, status TEXT, date_added TEXT' +
                      ', files TEXT, type TEXT, ep_order TEXT, del_watched BOOLEAN, num_eps INTEGER' +
                      ', ep_count INTEGER);')
            conn.commit()
            conn.close()
            Config.show_db_checked = True

    @staticmethod
    def get_id():
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        while True:
            id = ''
            for i in range(1, 7):
                id += random.randint(0, 9).__str__()
            ex_string = 'SELECT id FROM shows WHERE id = "' + id + '"'
            c.execute(ex_string)
            shows = c.fetchall()
            if shows.__len__() == 0:
                conn.commit()
                conn.close()
                return id


class PodcastFeed(Show):
    # Subclasses of Show must provide a way to get:
    # similar formatted 'info', name, show_page, desc, image for shows, type and
    # title, description, publish date in second, ep_file_url
    # parse_feed is the info builder, other classes should have their own info builder
    def __init__(self, feed_url):
        Show.__init__(self, feed_url)
        self.type = "podcast"
        if not self.in_db:
            print 'not in db'
            self.from_feed_by_url()


    def from_feed_by_url(self):  # used by constructor
        self.info = self.parse_feed()
        self.name = self.info['title']
        self.show_page = self.info['link']
        self.description = self.info['description']
        self.image = self.info['cover_url']
        self.id = Show.get_id()
        self.base_path = os.path.join(Config.library_path, self.name)
        for ep in self.info['episodes']:
            e = Episode(ep['title'], ep['description'],
                        ep['published'], ep['enclosures'][0]['url'],
                        self.image, self)
            if e not in self.episodes:
                self.episodes.append(e)

    def parse_feed(self):
        return podcastparser.parse(self.show_url, urllib2.urlopen(self.show_url))

    def update_from_url(self):
        # parse feed, rely on object, it was created from db, add new eps from feed not in eps[]
        self.info = self.parse_feed()
        for ep in self.info['episodes']:
            e = Episode(ep['title'], ep['description'],
                               ep['published'], ep['enclosures'][0]['url'],
                               self.image, self)
            if e not in self.episodes:
                self.episodes.append(e)
                e.add_to_db()

        # Make sure only eps marked available are downloaded
        avail_eps = []
        for e in self.episodes:
            if e.status == "available":
                avail_eps.append(e)

        num_eps_local = 0
        for e in self.episodes:
            if not not e.files["video"]:
                num_eps_local += 1
        eps_to_get = self.num_eps - num_eps_local

        if eps_to_get > 0:

            if eps_to_get > avail_eps.__len__():
                eps_to_get = avail_eps.__len__()
            avail_eps.sort()
            old_1st_order = range(-1, (eps_to_get + 1) * -1, -1)
            new_1st_order = range(eps_to_get)
            if self.order == "old_first":
                order = old_1st_order
            elif self.order == "new_first":
                order = new_1st_order
            for e in order:
                # print avail_eps[e].status
                avail_eps[e].status = "download"
                avail_eps[e].update_db()


class YouTubeChannel(Show):
    def __init__(self, channel_url):
        Show.__init__(self, channel_url)
        self.type = "youtube_channel"
        if not self.from_db_by_url():
            self.from_channel_by_url()

    def from_channel_by_url(self):
        pass

    def parse_channel(self):
        pass

    def update_from_url(self):
        # parse feed, check files on disk, check db entries
        self.info = self.parse_feed()


class Episode:
    statuses = ['available', 'download', 'downloading', 'download_error',
                'get_nfo', 'move', 'unwatched', 'watched', 'delete', 'deleted']

    def __init__(self, title, description, date, url, image, show):
        self.status = self.statuses[0]
        self.show = show
        self.title = title
        self.description = description
        self.image = image
        self.url = url
        self.date = date

        self.base_filename = self.get_base_filename()
        self.files = {}  # "video": '', 'image': '', 'nfo': ''
        self.prevent_deletion = False
        self.location = ''
        self.in_db = False

    @classmethod
    def from_db(cls, url):
        Episode.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute('SELECT * FROM episodes WHERE url = "' + url + '"')
        eps = c.fetchall()
        conn.commit()
        conn.close()
        if eps.__len__() > 0:
            title = eps[0][0]
            desc = eps[0][1]
            date = eps[0][2]
            image = eps[0][4]
            id = eps[0][5] # use to get show instance to pass to cls
            status = eps[0][6]
            base_filename = eps[0][7]
            files = eval(eps[0][8])
            prevent_deletion = eps[0][9]
            location = eps[0][10]
            show = Show.from_db_by_id(id)
            ep = cls(title, desc, date, url, image, show)
            ep.status = status
            ep.base_filename = base_filename
            ep.files = files
            ep.prevent_deletion = prevent_deletion
            ep.location = location
            ep.in_db = True
            return ep
        else:
            return None

    @staticmethod
    def get_eps_by_status(status):
        Episode.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute('SELECT url FROM episodes WHERE status = "' + status + '"')
        eps = c.fetchall()
        conn.commit()
        conn.close()
        found = []
        for e in eps:
            found.append(Episode.from_db(e[0]))
        return found

    @staticmethod
    def verify_db():
        if not Config.ep_db_checked:
            conn = sql.connect(Config.db)
            c = conn.cursor()
            c.execute('CREATE TABLE IF NOT EXISTS episodes(title TEXT' +
                      ', description TEXT, date INTEGER, url TEXT, image TEXT, id TEXT' +
                      ', status TEXT, base_filename TEXT, files TEXT' +
                      ', prevent_deletion Boolean, location TEXT);')
            conn.commit()
            conn.close()
            Config.ep_db_checked = True

    def __eq__(self, other):
        return self.__dict__['date'] == other.__dict__['date']

    def __lt__(self, other):
        return self.__dict__['date'] < other.__dict__['date']

    def __str__(self):
        return str(self.__dict__)

    def get_base_filename(self):
        return self.show.name + "-" + self.show.id + "-" + self.date.__str__()

    def write_metadata(self):
        # figure out path
        # in tmp, or from path of video if it exists
        path = Config.temp_path
        if self.location != '':
            path = self.location
        nfo_name = os.path.join(path, self.base_filename + '.nfo')

        image = ''
        if 'image' in self.files:
            image = self.files['image']

        t = Utils.get_time_tuple(self.date)
        # print t
        dashed_date = str(t.tm_year) + '-' + str(t.tm_mon) + '-' + str(t.tm_mday)
        # print dashed_date

        tv_show = ET.Element('tvshow')
        episode_fields = {
            'title': self.title,
            'season': str(t.tm_year),  # change year, season = year of ep release
            'episode': '0',                     # create ep count and use for ep number
            'plot': self.description,
            'thumb': image, #thumb should be local image location
            'genre': self.show.type,
            'premiered': dashed_date,
            'status': self.status,
            'aired': dashed_date,
            'studio': self.show.name,
            'url': self.url,
            'date': dashed_date,
            'prevent_deletion': self.prevent_deletion,
            'show_id': self.show.id,
            'base_filename': self.base_filename,
            'show_page': self.show.show_page,
            'show_url': self.show.show_url[0]
        }

        for f in episode_fields:
            x = ET.SubElement(tv_show, f)
            x.text = episode_fields[f]

        output_file = open(nfo_name, 'w')
        output_file.write(ET.tostring(tv_show))
        output_file.close()
        self.files['nfo'] = nfo_name
        self.status = 'move'
        self.update_db()

    def update_db(self):  # use after changing fields
        Show.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute("UPDATE episodes SET image=? WHERE url = ?", (self.image, self.url))
        c.execute("UPDATE episodes SET base_filename=? WHERE url = ?", (self.base_filename, self.url))
        c.execute("UPDATE episodes SET status=? WHERE url = ?", (self.status, self.url))
        c.execute("UPDATE episodes SET files=? WHERE url = ?", (repr(self.files), self.url))
        c.execute("UPDATE episodes SET title=? WHERE url = ?", (self.title, self.url))
        c.execute("UPDATE episodes SET description=? WHERE url = ?", (self.description, self.url))
        c.execute("UPDATE episodes SET prevent_deletion=? WHERE url = ?", (self.prevent_deletion, self.url))
        c.execute("UPDATE episodes SET location=? WHERE url = ?", (self.location, self.url))
        conn.commit()
        conn.close()

    def add_to_db(self):
        Episode.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        c.execute('SELECT id, date FROM episodes WHERE date = ' +
                  self.date.__str__() + ' AND id = ' + self.show.id)
        eps = c.fetchall()
        if eps.__len__() == 0:
            c.execute("INSERT INTO episodes VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);",
                      (self.title,  self.description, self.date, self.url,
                       self.image, self.show.id, self.status,
                       self.base_filename, repr(self.files),
                       self.prevent_deletion, self.location))
        conn.commit()
        conn.close()
        self.in_db = True

    def download_image(self):
        d = Download(self.base_filename, self.image)
        downloaded_file = d.download()
        if not downloaded_file:
            self.status = "download_error"
            self.update_db()
        else:
            self.files['image'] = os.path.join(Config.temp_path, downloaded_file)
            self.update_db()
            log('Episode image downloaded: %s' % downloaded_file)

    def download_video(self):
        d = Download(self.base_filename, self.url)
        downloaded_file = d.download()
        if not downloaded_file:
            self.status = "download_error"
            self.update_db()
        else:
            self.files['video'] = os.path.join(Config.temp_path, downloaded_file)
            log('Episode video downloaded: %s' % downloaded_file)

    def download(self):
        log.info('Writing show xml: '+ self.title)
        self.write_metadata()
        self.status = "downloading"
        self.location = Config.temp_path
        self.update_db()
        self.download_image()
        if self.status != 'download_error':
            self.download_video()
            if self.status != 'download_error':
                if 'image' in self.files and 'video' in self.files:
                    self.status = "move"
                    self.update_db()
                    log('Episode download complete: %s' % self.base_filename)
                    return True
        log.error('Error downloading file: %s' % self.base_filename)
        return False

    def move(self):
        for f in self.files:
            src_path = self.files[f]
            src_file = os.path.split(src_path)[1]
            dst_path = os.path.join(self.show.base_path, src_file)
            log.info('Moving file to show folder: ' + src_file)
            if os.path.exists(dst_path):
                log.warn('Destination file already exists, Deleting')
                os.remove(dst_path)
            os.rename(src_path, dst_path)
            self.files[f] = dst_path
            self.status = 'unwatched'
            self.update_db()


class Download:
    # https://gist.github.com/chandlerprall/1017266
    # http://stackoverflow.com/questions/13481276/threading-in-python-using-queue
    queue = Queue()

    def __init__(self, base_filename, url,):
        self.base_filename = base_filename
        self.url = url
        self.full_filename = self.base_filename + '.' + self.get_ext()
        self.file_path = os.path.join(Config.temp_path, self.full_filename)

    def get_ext(self):
        if self.url[-3:] in Config.accepted_extensions:
            return self.url[-3:]
        r = requests.get(self.url, stream=True)
        content_type = ''
        if 'content-type' in r.headers:
            content_type = r.headers['content-type']
        r.close()
        for ex in Config.accepted_extensions:
            if ex in content_type or ex in self.url:
                return ex
        if content_type.__len__() >= 3:
            return content_type[-3:]
        else:
            return ''

    @staticmethod
    def check_db_for_dls():
        Episode.verify_db()
        conn = sql.connect(Config.db)
        c = conn.cursor()
        ex_string = 'SELECT url FROM episodes WHERE status = "download"'
        c.execute(ex_string)
        eps = c.fetchall()
        conn.commit()
        conn.close()
        for e in eps:
            url = e[0]
            Download.queue.put(url)
        # Download.start_watchers()
        # time.sleep(3)
        # Download.queue.join() # figure out graceful shutdown later

    @staticmethod
    def start_watchers():
        for i in range(Config.download_threads):
            watcher = threading.Thread(target=Download.queue_watcher)
            # watcher.setDaemon(True)
            watcher.start()
        # Download.queue.join()

    @staticmethod
    def queue_watcher():
        print ' Starting download queue thread '
        while True:
            url = Download.queue.get()
            e = Episode.from_db(url)
            log.info('New download found: ' + url[20:])
            e.download()

    def download(self):
        Utils.verify_temp()
        dl_file = self.file_path + Config.dl_ext
        final_file = self.file_path
        # if os.path.exists(self.file_path + Config.dl_ext):
        #     output_file = open(self.file_path + Config.dl_ext, "ab")
        #     current_size = os.path.getsize(self.file_path + Config.dl_ext)
        #     resume_header = {'Range': 'bytes=%d-' % current_size}
        #     log.info('File Exists, Resuming Download at ' + str(current_size) + ' bytes')
        # else:
        output_file = open(dl_file, "wb")

        log.info('Beginning download: ' + self.full_filename)
        r = requests.get(self.url, stream=True)
        if r.status_code == 200:
            chunk_size = 2048
            with output_file as f:
                for chunk in r.iter_content(chunk_size):
                    f.write(chunk)
                f.close()
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            os.rename(dl_file, self.file_path)

            log.info('Download Complete: ' + self.full_filename)
            return self.full_filename
        else:
            log.error("Download Error, Code: %s" % r.status_code)
            log.error("url:  " + self.url)
            log.error("file: " + self.full_filename)
            return None


class Controller:
    # purpose: add_feed, check_feed, check_all_feeds,
    #          download_ep, get_ep_metadata
    def __init__(self, purpose, show=None, ep=None):
        if (purpose == "add_feed"):
            show.add_feed()
        elif (purpose == "update_feed"):
            show.update_from_url()
        elif (purpose == "check_all_feeds"):
            Show.update_all()
        elif (purpose == "download_shows"):
            Download.check_db_for_dls()
        # elif (purpose == "get_ep_metadata"):
        #     feed_checker(show)
        # elif (purpose == "check_feed"):
        #     feed_checker(show)

class Expire:
    def __init__(self):
        pass

class Scheduler:
    def __init__(self):
        pass

class Mover:
    def __init__(self):
        pass

class Plex:
    pass
    # check if ep played
    #     delete ep, related files
    #     trigger plex refresh on library
    # check if library exists
    # create plex library
    # allow for multiple libraries,
    #   and assigning shows to different libraries




class Utils:
    @staticmethod
    def get_time(time_in):
        return time.ctime(float(time_in))

    @staticmethod
    def get_time_tuple(time_in):
        return time.localtime(float(time_in))

    @staticmethod
    def verify_temp():
        if not os.path.exists(Config.temp_path):
            os.mkdir(Config.temp_path)

    def __init__(self):
        pass

class log:
    def __init__(self, msg):
        logging.debug(msg)

    @staticmethod
    def info(msg):
        logging.info(msg)

    @staticmethod
    def warn(msg):
        logging.warning(msg)

    @staticmethod
    def error(msg):
        logging.error(msg)

    @staticmethod
    def critical(msg):
        logging.critical(msg)

    @staticmethod
    def to_console():
        log_format = '%(asctime)s | %(threadName)-10s | %(message)s'
        logging.basicConfig(level=logging.DEBUG,
                            format=log_format,
                            datefmt='%H:%M:%S')

    @staticmethod
    def to_file():
        log_format = '%(asctime)s | %(threadName)-10s | %(message)s'
        logging.basicConfig(filename=Config.log_file,
                            level=logging.DEBUG,
                            format=log_format,
                            datefmt='%H:%M:%S')

if "__main__":
    log.to_console()
    main()
