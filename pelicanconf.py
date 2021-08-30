#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = 'Archive At Home Devs'
SITENAME = 'Archive At Home'
SITEURL = ''

THEME='themes/archive-at-home'
MENUITEMS = [('Tags', '/tags')]

PATH = 'content'

# Uncomment to enable caching to speed up rebuilds
# CACHE_CONTENT = True

TIMEZONE = 'America/Los_Angeles'

DEFAULT_LANG = 'en'

# Disable all feed generation
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

# Default number of results per page
DEFAULT_PAGINATION = 10

# Load custom reader for Ao3 downloaded html files.
PLUGINS = ['Ao3Reader']
READERS = {'html': 'Ao3Reader',
            'htm': 'Ao3Reader'}