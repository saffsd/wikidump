import sys
import csv
import os.path
import logging
import argparse 
import tempfile

from argparse import ArgumentParser

logger = logging.getLogger('wikidump')

import dataset
from utils import build_index, load_dumps, find_dumps
from model import Dump
from config import config


def c_list(args):
  """
  List available dumps.
  """
  dumps = find_dumps()
  # TODO: Print if an index exists
  for key in sorted(dumps):
    print "  %-20s%s" % (key, dumps[key])

def c_index(args):
  """
  Build index.
  """
  build_index()

def c_stats(args):
  """
  Output stats
  """
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

def c_categories(args):
    dump = load_dumps([args.language], build_index=True)[args.lang]
    cats = dump.categories

    for c in sorted(cats, key=lambda x:len(cats[x]), reverse=True):
      print "%-4d %s" % (len(cats[c]), c)

def main():
  parser = argparse.ArgumentParser()

  subparsers = parser.add_subparsers(help='available commands')

  list_subparser = subparsers.add_parser('list', help='list available dumps')
  list_subparser.set_defaults(func=c_list)

  index_subparser = subparsers.add_parser('index', help='builds indexes - (may take hours)')
  index_subparser.set_defaults(func=c_index)

  stats_subparser = subparsers.add_parser('stats', help='print statistics in a tab-delimited CSV format')
  stats_subparser.set_defaults(func=c_stats)

  categories_subparser = subparsers.add_parser('categories', help='categories info for a given language')
  categories_subparser.set_defaults(func=c_categories)
  categories_subparser.add_argument("language", help="Relevant language prefix")

  dataset_subparser = subparsers.add_parser('dataset', help='generate dataset by random sampling')
  dataset_subparser.set_defaults(func=dataset.randomsample)
  dataset_subparser.add_argument("-n", "--number", help="Number of files to select", type=int)
  dataset_subparser.add_argument("-t", "--temp", metavar='TEMPDIR', help="store temporary files in TEMPDIR")
  dataset_subparser.add_argument("--clean", action="store_true", default=False, help="apply heuristic mediawiki markup removal")
  dataset_subparser.add_argument("--minlen", help="Minimum length in bytes", type=int)
  dataset_subparser.add_argument("--skip_index", action="store_true", default=False, help="skip indexing stage, assumes indexing has already been performed")

  group = dataset_subparser.add_mutually_exclusive_group(required=True)
  group.add_argument("-l", "--language", action="append", help="Relevant language prefix")
  group.add_argument("--langs", help="path to a file containing a list of language prefixes") 

  dataset_subparser.add_argument("output", help="Output file (will be in tbz format)")
  args = parser.parse_args()

  # TODO: make the loglevel configurable
  logging.basicConfig(level=logging.INFO)

  # invoke subcommand
  args.func(args)


