"""
Model of a wikipedia dump
"""

import shelve 
import hashlib
import os
import re
import logging
import xml.etree.ElementTree as etree

import regexps
import utils
from config import config
from parser import PageOffsetParser


class Dump:
  logger = logging.getLogger('wikidump.model.Dump')

  def _open_shelf(self, name):
    "Open a shelf-file in a pre-determined location by name"
    path = os.path.join(self.cache_path, name)
    return shelve.open(path)

  def __init__(self, xml_path, build_index=False):
    self.xml_path = os.path.abspath(xml_path)
    self.xml_file = open(self.xml_path)
    # May want to hash the file instead for portability
    path_hash = hashlib.sha1(os.path.basename(self.xml_path)).hexdigest()
    self.cache_path = os.path.join(config.get('paths','scratch'), path_hash)

    self.logger.info("============================================")
    self.logger.info("Loading data for %s", self.xml_path)

    if not os.path.exists(self.cache_path):
      self.logger.info("Creating %s", self.cache_path)
      os.mkdir(self.cache_path)

    # Open a metadata shelf
    self.metadata = self._open_shelf('metadata')

    # Compute size of dump
    try:
      size = self.metadata['size']
    except KeyError:
      size = int(os.popen("grep '<page>' %s | wc -l" % self.xml_path).read())
      self.metadata['size'] = size
      self.logger.info("Found %d pages", size)
    self.logger.debug("Size: %d pages", size)

    # Mapping from page index to position in file
    self.page_offsets = self._open_shelf('page_offsets')
    #self.logger.debug("Currently know of %d page offsets", len(self.page_offsets))

    if build_index and len(self.page_offsets) < size:
      self.logger.info("Calculating page offsets")
      parser = PageOffsetParser(open(self.xml_path), self.page_offsets) 
      parser.run()
      self.page_offsets.sync()
    else:
      self.logger.debug("Not calculating page offsets")

    # Mapping from page title to page index
    self.page_titles = self._open_shelf('page_titles')
    #self.logger.debug("Currently know of %d page titles", len(self.page_titles))
    if build_index and len(self.page_titles) < size:
      self.logger.info("Building page title index")
      # Skip forwards if we ended up with a partial index due to an aborted 
      # build
      for i in range(len(self.page_titles),size):
        tree = etree.fromstring(self.get_raw(i))
        # Need to encode as etree will return both str and unicode
        title = tree.find('title').text.encode('utf8')
        if title in self.page_titles:
          self.logger.warning("Already had '%s', index %d", title, self.page_titles[title])
        else:
          self.page_titles[title] = i
    else:
      self.logger.debug("Not building page title index")

    # Mapping from categories to page indices 
    self.categories = self._open_shelf('categories')
    if build_index and 'categories_mapped' not in self.metadata: 
      self.logger.info("Building category index")
      cat_map = utils.category_map(self)
      # Copy into shelf
      for key in cat_map:
        self.categories[key] = cat_map[key]
      self.metadata['categories_mapped'] = True
    else:
      self.logger.debug("Not building category index")

    self.page_lengths = self._open_shelf('page_lengths')
    self.logger.debug("__init__ complete")

  def get_raw(self, index):
    "Get raw xml dump data for a given index"
    f = self.xml_file

    start_offset = self.page_offsets[str(index+1)]
    f.seek(start_offset)
    try:
      end_offset = self.page_offsets[str(index+2)]
      return f.read(end_offset - start_offset)
    except KeyError:
      # Handle the corner case which is the very last entry
      raw = f.read()
      match = re.search(r'.*</page>', raw)
      return raw[:match.end()]
      
  def get_page_index(self, title):
    "Look up the index of a page based on its title"
    return self.page_titles[title] 

  def get_page_contents(self, index):
    "Get the full text of a page by index"
    tree = etree.fromstring(self.get_raw(index))
    return tree.find('revision').find('text').text.encode('utf8')

  def get_page_length(self, index):
    "Look up the length of a page given an index"
    try:
      return self.page_lengths[str(index)]
    except KeyError:
      length = len(self.get_page_contents(index))
      self.page_lengths[str(index)] = length
      return length

  def get_page_contents_by_title(self, title):
    "Get the contents of a page with a given title"
    index = self.get_page_index(title)
    return self.get_page_contents(index)

  def get_page(self, title):
    "Return a Page object for the page of the given title"
    index = self.get_page_index(title)
    return Page(self.get_raw(index))

  def get_page_by_index(self, index):
    "Return a Page object given the raw index of the page"
    return Page(self.get_raw(index))

  def get_dumpfile_prefix(self):
    "Return the prefix code associated with the filename"
    filename = os.path.basename(self.xml_path)
    return regexps.dumpfile_name.match(filename).groups()[0]

class Page:
  """
  Represents a single page in a wikidump
  """
  logger = logging.getLogger('wikidump.model.Page')

  def __init__(self, string):
    """
    @param string: A string containin the raw xml version of the page
    """
    self.dom = etree.fromstring(string)
    self.text = self.dom.find('revision').find('text').text
    self.title = self.dom.find('title').text.encode('utf8')

    try:
      self.text = self.text.encode('utf8')
    except AttributeError:
      #self.logger.warning("Empty text!")
      self.text = ''

  def lang_equiv(self, prefix):
    """ Returns the page title for the equivalent page in the given language prefix
    """
    lang_links = dict(regexps.lang_link.findall(self.text))
    try:
      return lang_links[prefix]
    except KeyError:
      return None

  def categories(self):
    """ Returns the set of categories this page is member of.
        changed from 0.1 : was previously a list. Do not want duplicates.
    """
    try: 
      return set(zip(*regexps.category_link.findall(self.text))[0])
    except IndexError: #No categories
      return []

