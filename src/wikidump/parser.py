import logging
from sgmllib import SGMLParser

logger = logging.getLogger('wikidump.parser')

class PageOffsetParser(SGMLParser):
  "Parser to compute offsets for <page> starts by document index"
  def __init__(self, input_file, mapping):
    input_file.seek(0)
    self.input_file = input_file
    self.mapping = mapping
    self.current_offset = 0
    self.count = 0
    SGMLParser.__init__(self)

  def start_page(self, attrs):
    self.count += 1
    self.mapping[str(self.count)] = self.current_offset

  def run(self):
    for line in self.input_file:
      self.feed(line)
      self.current_offset += len(line)
