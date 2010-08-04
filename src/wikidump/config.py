import logging
from ConfigParser import SafeConfigParser

logger = logging.getlogger('wikidump.config')

config = SafeConfigParser()
if not config.read('wikidump.cfg'):
  print "Error!"
