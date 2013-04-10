"""
Code useful for preparing datasets from wikidump data
"""
import re
import os
import shutil

import logging
logger = logging.getLogger('wikidump.config')

import regexps
import utils
from config import config
from utils import load_dump

mediawiki_ignore_stringheads = '{}|=*#:'
def remove_mediawiki_syntax(text):
  "Remove non-content from a mediawiki page"
  text = regexps.redirect.sub('',text) # Remove redirects
  text = regexps.lang_link.sub('',text) # Remove language links
  text = regexps.template.sub('',text) # Remove templates TODO: Multi-line?
  text = regexps.intrawiki_link.sub(lambda x: x.group('anchor'), text) # Replace intrawiki links with anchor text
  text = re.sub('\n\n+', '\n\n', text) # Collapse multiple newlines
  para = paragraphs(text.strip()) # split into paragraphs

  content = []
  for p in para:
    p = re.sub('\s',' ', p)
    if regexps.langref.match(p): continue
    if regexps.assoc.match(p): continue
    if regexps.syntax.search(p): continue
    p = regexps.tripquote.sub('\g<name>',p)
    p = regexps.doubquote.sub('\g<name>',p)
    u = p.decode('utf8').strip()
    if regexps.category_name.search(u): continue
    content.append(u)

  retval = '\n\n'.join(u.encode('utf8') for u in content) + '\n'
  return retval

def paragraphs(text, minsize = 0):
  "Split text into paragraphs"
  return filter(lambda x: len(x) > minsize, text.split('\n\n'))

def lang_dist(langs):
  "mapping of the distribution of documents in a given set of languages"
  dumps = utils.load_dumps(langs)
  dist = dict((d.get_dumpfile_prefix(), d.metadata['size']) for d in dumps.values())
  return dist

try:
  import sampling
  from counter import Counter

  @sampling.CheckRNG
  def lang_sample(size, langs, rng=None):
    background = lang_dist(langs) 
    dist_raw = sampling.weighted_choice\
                 ( background
                 , count=size
                 , rng=rng
                 )

    dist = Counter(dist_raw)
    return dist 
except ImportError:
  # Skip if the sampling import fails - this will be because the numpy import in sampling failed
  pass

def refresh_dir(path):
  if os.path.exists(path) and not os.path.isdir(path):
    raise ValueError, "%s is not a directory" % path
  if os.path.exists(path):
    shutil.rmtree(path)
  os.mkdir(path)
  return path

import tarfile, subprocess, shutil, random, time, re
import regexps, tempfile
from cStringIO import StringIO

class ReTry(Exception): pass

def randomsample(args):
  """
  Produce a dataset by sampling.
  """

  if args.language:
    langs = args.language
  elif args.langs:
    langs = map(str.strip, open(args.langs))

  tempfile.tempdir = args.temp

  now = time.time()
  path = os.path.join(config.get('paths','scratch'), 'sample-{0}.tar'.format(args.number))
  build_index = not(args.skip_index)

  with tarfile.open(path, 'w') as tar:
    for lang in langs:
      try:
        dump = load_dump(lang, build_index=build_index, unpack=True)
      except KeyError:
        logger.error("do not have a dump for %s, skipping", lang)
        continue

      chosen = set() #keeps track of ids that have been chosen
      used = set() #keeps track of ids that have been examined
      
      # Adapted from wikicontent
      while len(chosen) < args.number:
        logger.debug("chose {0}/{1} so far".format(len(chosen), args.number))
        try:
          id = random.choice(xrange(dump.metadata['size']))
          if id in used:
            if len(used) >= dump.metadata['size']:
              # We have run out of documents to consider. Bail out.
              logger.warning("ran out of documents for %s", lang)
              break
            raise ReTry("already considered {0}".format(id))

          used.add(id)
          logger.debug("processing {0}".format(id))

          page = dump.get_page_by_index(id)

          if args.clean:
            # apply mediawiki removal
            text = remove_mediawiki_syntax(page.text)
            para = paragraphs(text)

            content = []
            for p in para:
              p = re.sub('\s',' ', p)
              if regexps.langref.match(p): continue
              if regexps.assoc.match(p): continue
              if regexps.syntax.search(p): continue
              p = regexps.tripquote.sub('\g<name>',p)
              p = regexps.doubquote.sub('\g<name>',p)
              u = p.decode('utf8').strip()
              if regexps.category_name.search(u): continue
              content.append(u)
            if not content: raise ReTry, "No usable content"

            document = '\n\n'.join(u.encode('utf8') for u in content) + '\n'
          else:
            # output raw mediawiki
            document = page.text

          if len(document) < args.minlen: 
            raise ReTry, "Too short ({0}<{1})".format(len(text), args.minlen)
          
          logger.debug("adding {0}".format(id))
          info = tarfile.TarInfo('{0}/{1}'.format(lang, id))
          info.size = len(document)
          info.mtime = now

          chosen.add(id)
          tar.addfile(info, StringIO(document))
          logger.debug("added {0}".format(id))

        except ReTry, e:
          logger.debug("Reject: %s", e.args[0])
          continue
      logger.info("chose %d documents for %s", len(chosen), lang)
      
  # Done with the tarfile, now to bzip it
  subprocess.call(['bzip2',path])
  shutil.move(path+'.bz2', args.output)
