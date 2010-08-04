import numpy
import random
import logging

from cPickle import dump

from utils import dumpSize, all_prefixes, page_parser
from parser import strip_mediawiki_markup

logger = logging.getLogger('wikidump.segment')

def create_dataset( num_doc
                  , distribution
                  , num_seg 
                  , text_transformer
                  , exclude = []
                  , seed = None
                  ):
  """
  Create a multilingual dataset from wikipedia data based on segments
  of monolingual documents.

  @param num_doc: number of documents in intended dataset
  @param distribution: Mapping from class name to proportion
  @param segments: Sequence of segments and their relative sizes
  @param exclude: Docids to be excluded from the final dataset
  """
  logger = logging.getLogger('wikidump.segment.create_dataset')
  logger.info('Creating dataset')
  docmap = {}
  classmap = {}
  # Set up a parser for each class
  parser = {}
  classlabels = []
  class_probs = numpy.empty( len(distribution), dtype=float) 
  dump_indices = [] 
  denominator = 0 
  logger.info('Setting up parsers')
  for i,classlabel in enumerate(distribution):
    parser[classlabel] = page_parser(classlabel)
    classlabels.append(classlabel)
    denominator += distribution[classlabel] 
    class_probs[i] = denominator 
    dumpsize = dumpSize(classlabel)
    indices = range(dumpsize)
    random.shuffle(indices)
    dump_indices.append(indices)
    logger.debug('Done for %s, %d indices', classlabel, dumpsize)
  logger.info('Parsers ready')

  # Normalize to a CDF
  class_probs /= denominator

  random.seed(seed)

  logger.info('Obtaining documents')
  for doc_num in range(num_doc):
    doc = ""
    classes = set() 
    segids = []
    for seg_num in range(num_seg):
      seg_class_index = numpy.searchsorted(class_probs, random.random())
      seg_class = classlabels[seg_class_index] 
      classes.add(seg_class)
      doc_index = dump_indices[seg_class_index].pop(0)
      segid = "_".join((seg_class, str(doc_index)))
      while segid in exclude:
        logger.debug('Ignored %s: in exclude', segid)
        try:
          doc_index = dump_indices[seg_class_index].pop(0)
        except IndexError:
          raise ValueError, "No more documents in class %s available" % classlabel 
        segid = "_".join((seg_class, str(doc_index)))
      segids.append(segid)
      content = text_transformer(parser[seg_class].get_entry(doc_index))
      seg_size = len(content)/num_seg
      seg_start = seg_size * seg_num
      seg_end = seg_start + seg_size
      doc += content[seg_start:seg_end] 
    docid = '-'.join(segids) 
    docmap[docid] = doc
    classmap[docid] = list(classes)
    logger.debug('Index: %d ID: %s', doc_num, docid)
  return docmap, classmap

if __name__ == "__main__":
  picklefile = open('segment.pickle', "w")
  distribution =  {}
  for p in all_prefixes:
    if len(p) > 3:
      logger.warning('Ignoring %s', p)
    else:
      distribution[p] = dumpSize(p)
  data = create_dataset( 5000 
                       , distribution 
                       , 2 
                       , strip_mediawiki_markup 
                       , exclude = []
                       , seed = 61383441363  
                       )
  dump(data, picklefile) 

