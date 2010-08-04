# Build all the indices we need 

import logging
logging.basicConfig(level=logging.INFO)

from wikidump.utils import load_dumps

if __name__ == "__main__":
  load_dumps(build_index=True)
  
