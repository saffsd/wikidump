import os
import logging
import time
import shelve

from config import config

scratchpath = config.get('paths','scratch')

class shelved(object):
  """ Decorator maker for shelved """
  def __init__(self, path):
    self.path = os.path.join(config.get('paths','scratch'), path)
    
  def __call__(self, func):
    return Shelved(self.path, func)

class Shelved(object):
   """Decorator that caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned, and
   not re-evaluated. Also shelves the result in the specified file for future
   use.
   """
   def __init__(self, shelf_path, func):
      self.func = func
      self.shelf = shelve.open(shelf_path)
      self.logger = logging.getLogger('wikidump.common.Shelved')

   def __del__(self):
      self.shelf.close() 

   def __call__(self, *args):
      key = str(args)
      try:
        return self.shelf[key]
      except KeyError:
        self.logger.debug("Not in cache: %s", key)
        self.shelf[key] = value = self.func(*args)
        return value
      except TypeError:
        # uncachable -- for instance, passing a list as an argument.
        # Better to not cache than to blow up entirely.
        self.logger.warning("Failed to cache")
        return self.func(*args)
   def __repr__(self):
      """Return the function's docstring."""
      return self.func.__doc__

