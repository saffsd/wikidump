from common import shelved
from utils import all_prefixes, raw_doc_lengths

@shelved("docs_under_thresh")
def docs_under_thresh(prefix, thresh):
  doc_lengths = raw_doc_lengths(prefix).values()
  return len(filter(lambda x: x < thresh, doc_lengths))

@shelved("indices_under_thresh")
def indices_under_thresh(prefix, thresh):
  doc_lengths = raw_doc_lengths(prefix).iteritems()
  return [ id for (id,len) in doc_lengths if len < thresh ]

def docids_under_thresh(prefixes, thresh):
  for prefix in prefixes:
    indices = indices_under_thresh(prefix, thresh)
    for index in indices:
      yield "_".join((prefix,str(index)))

