import sys
import csv
import os.path
import logging
import argparse 

logger = logging.getLogger('wikidump')

from utils import build_index, load_dumps, find_dumps
from model import Dump
from config import config

class ReTry(Exception): pass

def main():
  logging.basicConfig(level=logging.DEBUG)
  if len(sys.argv) < 2:
    logger.error("Must specify a command! Try 'help'")
    sys.exit(-1)

  command = sys.argv[1]

  if command == 'help':
    # Display a help message
    logger.info("The following commands are supported:")
    logger.info("    index             : builds indexes - warning: can take many hours")
    logger.info("    stats             : print statistics in a tab-delimited CSV format")
    logger.info("    categories [lang] : list categories for 'lang', and the number of documents in each")

  elif command == 'list':
    # List available dumps
    dumps = find_dumps()
    # TODO: Print if an index exists
    for key in sorted(dumps):
      print "  %-20s%s" % (key, dumps[key])
    
  elif command == 'index':
    # Build indices
    build_index()

  elif command == 'stats':
    root_logger = logging.getLogger()
    root_logger.level = logging.ERROR
    # Display statistics
    paths = find_dumps()
    sizes = dict((k, len(Dump(p))) for k, p in paths.iteritems())

    fields = ['lang', 'filename', 'pages', 'categories']
    outfile = csv.DictWriter(sys.stdout, fields)
    for p in sorted(sizes, key=sizes.get, reverse=True):
      dump = Dump(paths[p])
      d = dict\
            ( lang=p
            , filename=os.path.basename(paths[p])
            , pages=sizes[p]
            , categories=len(dump.categories)
            )
      outfile.writerow(d)

  elif command == 'categories':
    # Dump category distribution
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--language", dest="lang", help="Relevant language prefix")
    args = parser.parse_args(sys.argv[2:])

    dump = load_dumps([args.lang], build_index=True)[args.lang]
    cats = dump.categories

    for c in sorted(cats, key=lambda x:len(cats[x]), reverse=True):
      print "%-4d %s" % (len(cats[c]), c)

  elif command == 'sample':
    import tarfile, subprocess, shutil, random, time, re
    from cStringIO import StringIO

    import regexps
    import dataset
    # Sample a number of documents at random
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--language", action="append", help="Relevant language prefix")
    parser.add_argument("-n", "--number", help="Number of files to select", type=int)
    parser.add_argument("-o", "--output", help="Output file (will be in tbz format)", default="sample.tbz")
    parser.add_argument("--clean", action="store_true", default=False, help="apply heuristic mediawiki markup removal")
    parser.add_argument("--minlen", help="Minimum length in bytes", type=int)
    parser.add_argument("--langs", help="path to a file containing a list of language prefixes") 
    args = parser.parse_args(sys.argv[2:])

    if args.language and args.langs:
      parser.error("--langs and --language are mutually exclusive") 

    if args.language:
      langs = args.language
    elif args.langs:
      langs = map(str.strip, open(args.langs))
    else:
      raise ValueError("no languages to process")

    dumps = load_dumps(langs, build_index=True)

    now = time.time()
    path = os.path.join(config.get('paths','scratch'), 'sample-{0}.tar'.format(args.number))

    with tarfile.open(path, 'w') as tar:
      for lang in langs:
        dump = dumps[lang]

        chosen = set() #keeps track of ids that have been chosen
        used = set() #keeps track of ids that have been examined
        
        # Adapted from wikicontent
        while len(chosen) < args.number:
          logger.debug("chose {0}/{1} so far".format(len(chosen), args.number))
          try:
            id = random.choice(xrange(dump.metadata['size']))
            if id in used:
              raise ReTry("already considered {0}".format(id))

            used.add(id)
            logger.debug("processing {0}".format(id))

            page = dump.get_page_by_index(id)

            if args.clean:
              # apply mediawiki removal
              text = dataset.remove_mediawiki_syntax(page.text)
              para = dataset.paragraphs(text)

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
        
    # Done with the tarfile, now to bzip it
    subprocess.call(['bzip2',path])
    shutil.move(path+'.bz2', args.output)

  else:
    logging.error("Unknown command: %s", command)
    logging.info("Try the 'help' command.")
