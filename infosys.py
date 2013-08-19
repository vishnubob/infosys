#!/usr/bin/python

import vt220
import os
import time
import feedparser
import logging
import imp
import random
import traceback
import figlet
from config import Config
from optparse import OptionParser

# global Infosys Handle
InfoSysInstance = None

# base class for infotools, like the status bar, and the RSS feed
class InfoTool(object):
    Name = "__InfoTool__"

    def __init__(self, infosys):
        self.infosys = infosys

# RSS feed engine
class RSS(InfoTool):
    Name = "RSS"

    def __init__(self, infosys):
        super(RSS, self).__init__(infosys)
        self.feeds = Config.RSS.Feeds
        self.feed_cache = {}

    def refresh_feeds(self):
        fc = {}
        logging.debug("refesh_feeds(): refreshing %d feeds" % len(self.feeds))
        for feed in self.feeds:
            fc[feed] = feedparser.parse(self.feeds[feed].URL)
        self.feed_cache = fc

    def __getitem__(self, key):
        return self.feed_cache[key]

    def __contains__(self, key):
        return key in self.feed_cache

    def keys(self):
        return self.feed_cache.keys()

    def get_feed_name(self, feed):
        return self.feeds[feed].name

# engine for displaying RSS feeds
class RSSDisplay(InfoTool):
    def __init__(self, infosys):
        super(RSSDisplay, self).__init__(infosys)
        self.feed_stack = []

    # build a list of RSS feeds to show
    def update_feed_stack(self):
        rss = self.infosys.registry.RSS
        rss.refresh_feeds()
        rsskeys = rss.keys()
        # weather is handled by a different widget
        # XXX: general filtering?
        if 'weather' in rsskeys:
            del rsskeys[rsskeys.index('weather')]
        # shuffle the feed order
        deck = []
        for key in rsskeys:
            feed = rss[key]
            for entry in feed.entries:
                deck.append((key, entry))
        self.feed_stack = []
        logging.debug("update_feed_stack(): shuffling %d feed entries"% len(deck))
        random.shuffle(deck)
        for entry in deck:
            self.feed_stack.append(entry)
        #while deck:
        #   entry = random.choice(deck)
        #   del deck[deck.index(entry)]
        #   self.feed_stack.append(entry)

    def _format_text(self, text, page):
        ts = vt220.TypeSetter()
        ts.set_margins((0, 160, 1, 25))
        ts.set_textflow(ts.DOWN)
        fonts = self.infosys.registry.Fonts
        fonts = [f[0] for f in fonts]
        random.shuffle(fonts)
        ts.format_text(text, fonts, page)

    def format_summary(self, title, summary, page):
        # title
        ts = vt220.TypeSetter()
        ts.set_margins((0, 80, 2, 25))
        ts.set_textflow(ts.DOWN)
        fonts = self.infosys.registry.Fonts
        fonts = [f[0] for f in fonts]
        random.shuffle(fonts)
        ts.format_text(title, fonts, page)
        # summary
        ts = vt220.TypeSetter()
        ts.set_margins((82, 158, 2, 25))
        summary = summary.encode('ascii', 'ignore')
        ts.raw_format(summary, page)
        
    def format_title(self, title, page):
        ts = vt220.TypeSetter()
        ts.set_margins((0, 160, 2, 25))
        ts.set_textflow(ts.DOWN)
        fonts = self.infosys.registry.Fonts
        fonts = [f[0] for f in fonts]
        random.shuffle(fonts)
        ts.format_text(title, fonts, page)
        
    def draw(self, page):
        if not self.feed_stack:
            self.update_feed_stack()
        feedname, entry = self.feed_stack.pop()
        rss = self.infosys.registry.RSS
        ib = self.infosys.registry.InfoBar
        feedname = rss.get_feed_name(feedname)
        ib.set_banner("Feed: %s" % feedname)
        title = entry['title']
        print title
        if 'summary' in entry:
            try:
                summary = entry['summary']
                if "<" in summary:
                    idx = summary.find("<")
                    summary = summary[:idx].strip()
                self.format_summary(title, summary, page)
            except:
                self.format_title(title, page)
        else:
            self.format_title(title, page)

class Weather(InfoTool):
    Name = "Weather"

    def __init__(self, infosys):
        super(Weather, self).__init__(infosys)
        self.current_condition = "unknown"
        self.current_temperature = "?? F"
        self.forecast = []

    def update(self):
        rss = self.infosys.registry.RSS
        if "weather" not in rss:
            return False
        try:
            weather = rss['weather']['entries'][0]['summary']
        except:
            print "Weather update failed."
            return False
        cc = False
        fc = False
        self.forecast = []
        for line in weather.split('\n'):
            if "Current Conditions" in line:
                cc = True
                continue
            if "Forecast" in line:
                fc = True
                continue
            if cc:
                line = line[0:line.find('<')]
                txt, temp = line.split(',')
                txt = txt.strip()
                temp = temp.strip()
                self.current_condition = txt
                self.current_temperature = temp
                cc = False
            if fc:
                line = line[0:line.find('<')]
                line = line.strip()
                self.forecast.append(line)
                if not line:
                    break
        return True

class InfoBar(InfoTool):
    Name = "InfoBar"
    clock_format = Config.InfoBar.ClockFormat
    banner = 'InfoSys 0.1'
    
    def set_banner(self, banner):
        self.banner = banner
    
    def switch_up(self):
        braces = (("[[", "]]"), ("((", "))"), ("**", "**"), ("{{", "}}"))
        brace = random.choice(braces)
        item1 = "%(Clock)s        %(Weather)s"
        item2 = "%(Banner)s"
        items = [item1, item2]
        random.shuffle(items)
        self.infobar_head = "%s %s" % (brace[0], items[0])
        self.infobar_tail = "%s %s" % (items[1], brace[1])

    def draw(self, page):
        # weather
        weather = self.infosys.registry.Weather
        weather.update()
        cc = weather.current_condition
        temp = weather.current_temperature
        # page
        page.set_cursor(0, 0)
        # dictionary
        ibd = {}
        ibd['Clock'] = time.strftime(self.clock_format, time.localtime())
        ibd['Banner'] = self.banner
        ibd['Weather'] = "%s, %s" % (cc,temp)
        # substitution
        self.switch_up()
        tail = self.infobar_tail % ibd
        head = self.infobar_head % ibd
        indent = vt220.WIDTH - len(tail)
        bar = head.ljust(indent) + tail
        page.write(bar)
        return page

class Registry(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def scan_libraries(self):
        self.Transitions = self.__class__()
        self.Images = self.__class__()
        self.Animations = self.__class__()
        for lib in Config.Registry.Library:
            logging.debug("scan_libraries(): scanning '%s'" % lib)
            mname = Config.Registry.Library[lib]
            module = imp.load_module(mname, *imp.find_module(mname))
            for cls in module.__dict__:
                cls = module.__dict__[cls]
                try:
                    if issubclass(cls, vt220.Image):
                        self.Images[cls.__name__] = cls
                        continue
                    if issubclass(cls, vt220.Transition):
                        self.Transitions[cls.__name__] = cls
                        continue
                    if issubclass(cls, vt220.Animation):
                        self.Animations[cls.__name__] = cls
                        continue
                except TypeError:
                    continue
            objcnt = len(self.Images) + len(self.Transitions)
            logging.debug("scan_libraries(): found %d objects" % objcnt)

class InfoSys(object):
    def __init__(self):
        self.running = False

    def get_infosys(cls):
        return cls.instance
    get_infosys = classmethod(get_infosys)

    def set_infosys(cls, instance):
        cls.instance = instance
    set_infosys = classmethod(set_infosys)

    def startup(self):
        self.initialize_logging()
        logging.debug("startup(): initializing InfoSys")
        self.initialize_registry()
        self.initialize_infotools()
        self.initialize_display()
        self.initialize_misc()
        logging.debug("startup(): finished initializing InfoSys")

    def shutdown(self):
        logging.debug("shutdown(): shutting down InfoSys.")
        self.display = None
        self.running = False
        time.sleep(5)

    def initialize_misc(self):
        ff = figlet.FigletFormatter()
        self.registry.Fonts = ff.get_fonts()
    
    def initialize_display(self):
        df = vt220.DisplayFactory(self.socket_flag)
        self.display = vt220.Display()

    def initialize_infotools(self):
        self.registry.RSS = RSS(self)
        self.registry.Weather = Weather(self)
        self.registry.InfoBar = InfoBar(self)
        self.registry.RSSDisplay = RSSDisplay(self)

    def initialize_registry(self):
        self.registry = Registry()
        self.registry.scan_libraries()
        
    def initialize_logging(self):
        logging.basicConfig(level=Config.Logging.Level,
                        format=Config.Logging.Format,
                        filename=Config.Logging.LogFileName,
                        filemode='a')
        console = logging.StreamHandler()
        console.setLevel(Config.Logging.Level)
        formatter = logging.Formatter(Config.Logging.Format)
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger().addHandler(console)

    def start(self, socket=False):
        self.socket_flag = socket
        self.startup()
        self.running = True
        while self.running:
            try:
                self.run()
            finally:
                self.shutdown()

    def run(self):
        current_page = vt220.Page()
        img = self.registry.Images['StartupImage']
        img = img()
        self.display.open()
        self.display.clear_screen()
        img.draw(current_page)
        self.display.draw(current_page)
        time.sleep(30)
        while True:
            self.display.reboot()
            newpage = vt220.Page()
            if random.random() < .1:
                img = random.choice(self.registry.Images.values())
                img = img()
                img.draw(newpage)
            else:
                self.registry.RSSDisplay.draw(newpage)
            self.registry.InfoBar.draw(newpage)
            trcls = random.choice(self.registry.Transitions.values())
            tr = trcls(current_page, newpage)
            pages = []
            for page in tr:
                pages.append(page)
            for page in pages:
                self.display.draw(page)
            current_page = page
            time.sleep(30)

class InfoSysSingleton:
    __instance = None

    def __init__(self):
        if InfoSysSingleton.__instance is None:
            InfoSysSingleton.__instance = InfoSys()

        # Store instance reference as the only member in the handle
        self.__dict__['_InfoSysSingleton__instance'] = InfoSysSingleton.__instance

    def __getattr__(self, attr):
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        return setattr(self.__instance, attr, value)

def get_infosys():
    return InfoSysSingleton()

def parse_args():
    parser = OptionParser()
    parser.add_option('--socket', 
        dest='socket', help='Socket Debug Mode', action="store_true")
    parser.set_defaults(socket=False)
    return parser.parse_args()

if __name__ == '__main__':
    opts, args = parse_args()
    isys = InfoSysSingleton()
    try:
        isys.start(opts.socket)
    finally:
        if opts.socket:
            os.unlink('display.socket')
