import sys
import csv
import os.path
import logging
import optparse
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger('wikidump')

from wikidump.utils import load_dumps

def main():
  if len(sys.argv) < 2:
    logger.error("Must specify a command!")
    sys.exit(-1)

  command = sys.argv[1]

  if command == 'help':
    # Display a help message
    logger.info("The following commands are supported:")
    logger.info("    index             : builds indexes - warning: can take many hours")
    logger.info("    stats             : print statistics in a tab-delimited CSV format")
    logger.info("    categories [lang] : list categories for 'lang', and the number of documents in each")

  elif command == 'index':
    # Build indices
    load_dumps(build_index=True)

  elif command == 'stats':
    # Display statistics
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.ERROR)

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

  elif command == 'categories':
    # Dump category distribution
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.ERROR)

    parser = optparse.OptionParser()
    parser.add_option("-l", "--language", dest="lang", help="Relevant language prefix")
    options, args = parser.parse_args(sys.argv[2:])

    dump = load_dumps([options.lang], build_index=True)[options.lang]
    cats = dump.categories

    for c in sorted(cats, key=lambda x:len(cats[x]), reverse=True):
      print "%-4d %s" % (len(cats[c]), c)

  else:
    logging.error("Unknown command: %s", command)
    logging.info("Try the 'help' command.")
