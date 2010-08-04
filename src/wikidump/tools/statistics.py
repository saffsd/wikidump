# Print a table of statistics of dumps that we have

import csv
import sys
import os.path
import logging
logging.basicConfig(level=logging.ERROR)

from wikidump.utils import load_dumps

if __name__ == "__main__":
  dumps = load_dumps()
  sizes = dict((d.get_dumpfile_prefix(), d.metadata['size']) for d in dumps.values())

  fields = ['lang', 'filename', 'pages', 'categories']
  outfile = csv.DictWriter(sys.stdout, fields, delimiter='\t')
  for p in sorted(sizes, key=sizes.get, reverse=True):
    d = dict\
          ( lang=p
          , filename= os.path.basename(dumps[p].xml_path)
          , pages=sizes[p]
          , categories=len(dumps[p].categories)
          )
    outfile.writerow(d)
    
