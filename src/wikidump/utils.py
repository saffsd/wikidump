import os
import re
import logging

from collections import defaultdict

from config import config
import model
import regexps

logger = logging.getLogger('wikidump.utils')

xml_path = config.get('paths','xml_dumps')

def find_dumps(path):
  def visit(arg, dirname, names):
    for name in names:
      match = regexps.dumpfile_name.match(name)
      if match:
        arg.append(os.path.join(dirname, name))

  paths = []
  os.path.walk(path, visit, paths)

  dump_paths = {}
  for p in paths:
    match = regexps.dumpfile_name.search(os.path.basename(p))
    if match.group('prefix') in langs:
      dump_paths[match.group('prefix')] = p
  return dump_paths

def load_dumps(langs=None, dump_path=None, build_index=False):
  "Load the dumps, and take note of their size"
  # Take note that we will end up loading all the dumps we have for a given language
  # but only returning the last one we find. 
  # TODO: Handle different-dated dumps of the same language
  if langs is None:
    langs = all_prefixes
  if dump_path is None:
    dump_path = xml_path
  dumps = {}
  for path in os.listdir(dump_path):
    if not re.match('|'.join(langs), path): continue
    full_path = os.path.join(dump_path, path)
    d = model.Dump(full_path, build_index=build_index)
    prefix = d.get_dumpfile_prefix() 
    dumps[prefix] = d
  return dumps

def category_map(dump):
  "Compute the category mapping of a particular dump"
  cat_count = defaultdict(list)
  for i in xrange(dump.metadata['size']):
    p = dump.get_page_by_index(i)
    for c in p.categories():
      cat_count[c].append(i)
  return cat_count
