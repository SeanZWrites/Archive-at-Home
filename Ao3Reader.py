"""
AO3 HTML Parser

Original code for HTML parsing (c) Pelican Contributors 
(https://github.com/getpelican/pelican)

Additional work for AO3 parsing (c) Sean Z.
"""

from pelican.readers import BaseReader
from pelican.utils import pelican_open
from markdown import Markdown
from html.parser import HTMLParser
from html import escape, unescape
import logging
from pelican import signals

logger = logging.getLogger(__name__)

class Ao3Reader(BaseReader):
    """Parses HTML files as input, looking for meta, title, and body tags"""

    file_extensions = ['htm', 'html']
    enabled = True

    class Ao3Parser(HTMLParser):

        # TODO:
        # - Fix author parsing

        def __init__(self, settings, filename):
            super().__init__(convert_charrefs=False)
            self.body = ''
            self.metadata = {
                "date": "2019-01-31",  
                'tags': [],
                'category': 'Fic',
                'authors': [],
                'summary': ''
            }

            self.settings = settings

            self._data_buffer = ''

            self._filename = filename

            self._in_meta = False
            self._meta_divs = 0
            self._in_title = False
            self._in_author = False
            self._in_summary = False
            self._in_content = False
            self._in_tags = False
            self._in_tag_prefix = False
            self._tag_prefix = ""
            self._in_tag = False

        def handle_starttag(self, tag, attrs):

            # meta contains tag data, authors, and title (_in_meta)
            if tag == 'div' and self._attr_value(attrs, 'class') == "meta" and not self._in_content:
                logging.debug("entered meta, meta divs are %d", self._meta_divs)
                self._in_meta = True

            # the meta can have extra divs - track how many there are so we don't end meta too
            # early (since end tags don't have attrs)
            elif tag == 'div' and self._in_meta:
                self._meta_divs += 1
                logging.debug("meta count is %d", self._meta_divs)

            # extract the summary, which is the first block quote in the meta div
            elif tag == 'blockquote' and self._in_meta and not self.metadata['summary']:
                self._data_buffer = ''
                self._in_summary = True

            # the main div with id chapters is the document body (_in_content)
            elif tag == 'div' and self._attr_value(attrs,'id') == "chapters":
                self._in_content = True
                self._data_buffer = ''

            # used for detecting the start of the tag block
            elif tag == 'dl' and self._attr_value(attrs, 'class') == 'tags':
                self._in_tags = True

            # used for detecting the tag group name (Fandoms, Characters, Additional Tags)
            elif tag == 'dt' and self._in_tags:
                self._in_tag_prefix = True
                self._data_buffer = ''

            # used for processing the beginning of a group of tags within a group
            elif tag == 'dd' and self._in_tags:
                self._in_tag = True
                self._data_buffer = ''

            # used for detecting an individual tag text
            elif tag == 'a' and self._in_tag:
                self._data_buffer = ''

            # detect individual authors
            elif tag == 'a' and self._attr_value(attrs, 'rel') == 'author':
                self._in_author = True
                self._data_buffer = ''
        
            # detect title
            elif tag == 'h1' and self._in_meta:
                self._in_title = True
                self._data_buffer = ''

            elif self._in_content:
                self._data_buffer += self.build_tag(tag, attrs, False)

        def handle_endtag(self, tag):
            if tag == 'div' and self._in_meta:
                if self._meta_divs == 0: 
                    self._in_meta = False
                    logging.debug("exitted meta")

                    # fix isuses with authors if they aren't set at this point
                    # (happens if the work was anonymous)
                    if len(self.metadata['authors']) == 0: self.metadata['authors'].append("Anonymous")

                else:
                    self._meta_divs -= 1
                    logging.debug("meta count is %d", self._meta_divs)
                
            elif tag == 'blockquote' and self._in_summary:
                self._in_summary = False
                summary = self._data_buffer.strip()
                logging.debug('Set summary to: %s', summary)
                self.metadata['summary'] = summary

            elif tag == 'body':
                self.body = self._data_buffer
                self._in_content = False

            elif tag == 'dl' and self._in_tags:
                self._in_tags == False

            elif tag == 'dt' and self._in_tags:
                self._in_tag_prefix = False
                self._tag_prefix = self._data_buffer.strip()
                logger.debug("Setting tag prefix to: %s", self._tag_prefix)

            elif tag == 'dd' and self._in_tags:
                self._in_tag = False

                # parse the stat block for date
                # it probably makes more sense to handle this with a regex
                if self._tag_prefix == 'Stats:':
                    stat_block = self._data_buffer.strip()
                    stats = stat_block.split('\n')
                    for stat in stats:
                        if 'Published' in stat:
                            self.metadata['date'] = stat.split(" ")[-1]
                            break

            elif tag == 'a' and self._in_tag:
                if self._tag_prefix != 'Stats:':
                    tag = self._tag_prefix + unescape(self._data_buffer.strip())
                    logger.debug("Setting tag to: %s", tag)
                    self.metadata['tags'].append(tag)

            elif tag == 'a' and self._in_author:
                self._in_author = False
                author_name = self._data_buffer.strip()
                logging.debug("Adding author: %s", author_name)
                self.metadata['authors'].append(author_name)

            elif tag == 'h1' and self._in_title:
                self._in_title = False
                title = self._data_buffer.strip()
                logging.debug("Setting title to %s", title)
                self.metadata['title'] = title

            elif self._in_content:
                self._data_buffer += '</{}>'.format(escape(tag))

        def handle_startendtag(self, tag, attrs):
            if self._in_content:
                self._data_buffer += self.build_tag(tag, attrs, True)

        def handle_comment(self, data):
            self._data_buffer += '<!--{}-->'.format(data)

        def handle_data(self, data):
            self._data_buffer += data

        def handle_entityref(self, data):
            self._data_buffer += '&{};'.format(data)

        def handle_charref(self, data):
            self._data_buffer += '&#{};'.format(data)

        def build_tag(self, tag, attrs, close_tag):
            result = '<{}'.format(escape(tag))
            for k, v in attrs:
                result += ' ' + escape(k)
                if v is not None:
                    # If the attribute value contains a double quote, surround
                    # with single quotes, otherwise use double quotes.
                    if '"' in v:
                        result += "='{}'".format(escape(v, quote=False))
                    else:
                        result += '="{}"'.format(escape(v, quote=False))
            if close_tag:
                return result + ' />'
            return result + '>'

        @classmethod
        def _attr_value(cls, attrs, name, default=None):
            return next((x[1] for x in attrs if x[0] == name), default)

    def read(self, filename):
        """Parse content and metadata of HTML files"""
        with pelican_open(filename) as content:
            parser = self.Ao3Parser(self.settings, filename)
            parser.feed(content)
            parser.close()

        metadata = {}
        for k in parser.metadata:
            metadata[k] = self.process_metadata(k, parser.metadata[k])
        return parser.body, metadata

def add_reader(readers):
    readers.reader_classes['html'] = Ao3Reader
    readers.reader_classes['htm'] = Ao3Reader

# This is how pelican works.
def register():
    signals.readers_init.connect(add_reader)