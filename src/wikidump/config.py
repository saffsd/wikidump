import logging
from ConfigParser import SafeConfigParser

logger = logging.getLogger('wikidump.config')

default_config_path = 'wikidump.cfg'

config = SafeConfigParser()

if not config.read(default_config_path):
  logger.info("Did not find a configuration file. Creating one.")
  config.add_section('paths')
  config.set('paths', 'scratch', '/tmp')
  config.set('paths', 'xml_dumps', '/path/to/dumps')
  with open(default_config_path, 'w') as configfile:
    config.write(configfile)

