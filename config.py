#!/usr/bin/python
import logging

class ConfigDictionary(dict):
    def __getattr__(self, name):
        if name not in self:
            self[name] = ConfigDictionary()
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

Config = ConfigDictionary()

## RSS
# refresh rate in second
Config.RSS.Refresh = 60 * 10

# Weather
Config.RSS.Feeds.weather.name = "Somerville Weather"
Config.RSS.Feeds.weather.URL = \
    'http://xml.weather.yahoo.com/forecastrss?p=02143&u=f'
Config.RSS.Feeds.weather.priority = 1

# NYTimes Feed
Config.RSS.Feeds.nytimes.name = "New York Times"
Config.RSS.Feeds.nytimes.URL = \
    'http://www.nytimes.com/services/xml/rss/nyt/HomePage.xml'
Config.RSS.Feeds.nytimes.priority = 2

# NYTimes Feed - science 
Config.RSS.Feeds.nysci.name = "New York Times - Science"
Config.RSS.Feeds.nysci.URL = \
    'http://www.nytimes.com/services/xml/rss/nyt/Science.xml'
Config.RSS.Feeds.nysci.priority = 2

# NYTimes Feed - science earth
Config.RSS.Feeds.nysciearth.name = "New York Times - Science Earth"
Config.RSS.Feeds.nysciearth.URL = \
    'http://www.nytimes.com/services/xml/rss/nyt/Environment.xml'
Config.RSS.Feeds.nysciearth.priority = 2

# BoingBoing Feed
Config.RSS.Feeds.boingboing.name = "BoingBoing"
Config.RSS.Feeds.boingboing.URL = \
    'http://feeds.feedburner.com/boingboing/iBag'
Config.RSS.Feeds.boingboing.priority = 3

# Slashdot Feed
Config.RSS.Feeds.slashdot.name = "Slashdot"
Config.RSS.Feeds.slashdot.URL = 'http://rss.slashdot.org/Slashdot/slashdot'
Config.RSS.Feeds.slashdot.priority = 3

# CNN - Top Stories
Config.RSS.Feeds.cnntop.name = "CNN - Top Stories"
Config.RSS.Feeds.cnntop.URL = 'http://rss.cnn.com/rss/cnn_topstories.rss'
Config.RSS.Feeds.cnntop.priority = 3

# CNN - World Stories
Config.RSS.Feeds.cnnworld.name = "CNN - World Stories"
Config.RSS.Feeds.cnnworld.URL = 'http://rss.cnn.com/rss/cnn_world.rss'
Config.RSS.Feeds.cnnworld.priority = 3

# CNN - US Stories
Config.RSS.Feeds.cnnus.name = "CNN - World Stories"
Config.RSS.Feeds.cnnus.URL = 'http://rss.cnn.com/rss/cnn_us.rss'
Config.RSS.Feeds.cnnus.priority = 3

# BBC - Headlines
Config.RSS.Feeds.bbctop.name = "BBC - Top Stories"
Config.RSS.Feeds.bbctop.URL = \
    'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/front_page/rss.xml'
Config.RSS.Feeds.bbctop.priority = 3

# BBC - Science and Technology
Config.RSS.Feeds.bbcscitech.name = "BBC - Science and Technology"
Config.RSS.Feeds.bbcscitech.URL = \
    'http://newsrss.bbc.co.uk/rss/newsonline_uk_edition/sci/tech/rss.xml'
Config.RSS.Feeds.bbcscitech.priority = 3

# Comedy Central - Joke of the Day
Config.RSS.Feeds.ccjotd.name = "Comedy Central - Joke of the Day"
Config.RSS.Feeds.ccjotd.URL = \
    'http://www.comedycentral.com/rss/jokes/index.jhtml'
Config.RSS.Feeds.ccjotd.priority = 3

# Comedy Central - Daily Show Headlines
Config.RSS.Feeds.ccdshl.name = "Comedy Central - Daily Show Headlines"
Config.RSS.Feeds.ccdshl.URL = \
    'http://www.comedycentral.com/rss/tdsheadlines.jhtml'
Config.RSS.Feeds.ccdshl.priority = 3

# AP News - Strange
Config.RSS.Feeds.apnews_strange.name = "Associated Pressed - Strange"
Config.RSS.Feeds.apnews_strange.URL = \
    'http://hosted.ap.org/lineups/STRANGEHEADS-rss_2.0.xml?SITE=MATAU&SECTION=HOME'
Config.RSS.Feeds.apnews_strange.priority = 3

# AP News - Top News
Config.RSS.Feeds.apnews_topnews.name = "Associated Pressed - Top News"
Config.RSS.Feeds.apnews_topnews.URL = \
    'http://hosted.ap.org/lineups/TOPHEADS-rss_2.0.xml?SITE=NCJAC&SECTION=HOME'
Config.RSS.Feeds.apnews_topnews.priority = 3

# boston.com - Local News
Config.RSS.Feeds.boston_toplocal.name = "boston.com - Local News"
Config.RSS.Feeds.boston_toplocal.URL = \
    'http://feeds.boston.com/boston/news/local'
Config.RSS.Feeds.boston_toplocal.priority = 1

## InfoBar
# cock format
Config.InfoBar.ClockFormat = "%A, %B %d %Y - %I:%M %p"

# Logging
Config.Logging.Format = '%(asctime)s %(levelname)s %(message)s'
Config.Logging.Level = logging.DEBUG
Config.Logging.LogFileName = 'infosys.txt'

Config.Registry.Library.content = 'content'
