"""
Code useful for preparing datasets from wikidump data
"""
import re

import regexps
import utils

mediawiki_ignore_stringheads = '{}|=*#:'

def remove_mediawiki_syntax(text):
  "Remove non-content from a mediawiki page"
  text = regexps.redirect.sub('',text) # Remove redirects
  text = regexps.lang_link.sub('',text) # Remove language links
  text = regexps.template.sub('',text) # Remove templates TODO: Multi-line?
  text = regexps.intrawiki_link.sub(lambda x: x.group('anchor'), text) # Replace intrawiki links with anchor text
  text = re.sub('\n\n+', '\n\n', text) # Collapse multiple newlines
  return text.strip()

def paragraphs(text, minsize = 0):
  "Split text into paragraphs"
  return filter(lambda x: len(x) > minsize, text.split('\n\n'))

def lang_dist(langs):
  "mapping of the distribution of documents in a given set of languages"
  dumps = wikidump.load_dumps(langs)
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


