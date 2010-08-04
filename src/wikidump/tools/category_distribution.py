# Compute the distribution of categories in different langauges

import optparse
import logging
logging.basicConfig(level=logging.ERROR)

from wikidump.utils import load_dumps, category_map

if __name__ == "__main__":
  parser = optparse.OptionParser()
  parser.add_option("-l", "--language", dest="lang", help="Relevant language prefix")
  options, args = parser.parse_args()

  dumps = load_dumps([options.lang], build_index=True)

  dump = dumps[options.lang]

  cats = dump.categories

  for c in sorted(cats, key=lambda x:len(cats[x]), reverse=True):
    print "%-4d %s" % (len(cats[c]), c)
    
