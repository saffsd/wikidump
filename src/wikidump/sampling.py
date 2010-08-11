"""
Provides numpy-based routines for performing sampling tasks
"""
import numpy
import math

allow_default_rng = True
default_rng = numpy.random.mtrand.RandomState()

class RNGError(Exception): pass

class CheckRNG(object):
  """ Decorator that checks that an RNG has been provided, or provides a default one 
      if it is allowed by the module's current setting, as controlled by the 
      'allow_default_rng' variable
  """
  def __init__(self, func):
    self.func = func

  def __call__(self, *args, **kwargs):
    if 'rng' not in kwargs or kwargs['rng'] is None:
      if allow_default_rng:
        kwargs['rng'] = default_rng
      else:
        raise RNGError, "Default RNG disabled - please pass an explicit RNG"
    return self.func(*args, **kwargs)

  def __repr__(self):
    return repr(self.func)

  def __str__(self):
    return str(self.func)

@CheckRNG
def weighted_choice(items, weights=None, count=1, rng=None):
  """ Weighted random choice of n items
  """
  if hasattr(items, 'values'): 
    items, weights = zip(*items.items())
   
  if not weights: weights = len(items) * [1]

  # Normalize to 1 if required
  t = float(sum(weights))

  # Uniform chance if weights sum to 0
  if t == 0.0: weights = [ 1/len(items) for i in items ]
  elif t != 1.0: weights = [ w/t for w in weights ]

  dist = numpy.cumsum(weights)
  result = numpy.searchsorted(dist, rng.random_sample(count))

  if count == 1:
    return list(numpy.array(items)[result])[0]
  else:
    return list(numpy.array(items)[result])

@CheckRNG
def partition(num_items, weights, probabilistic = False, rng = None):
  """
  Partition a number of items into partitions according to weights
  Modified from hydrat: http://hydrat.googlecode.com/svn/trunk/task/sampler.py
  @return: map of doc_index -> partition membership
  @rtype: numpy boolean array (items * partitions)
  """
  weights = numpy.array(weights)
  probabilities = weights / float(numpy.sum(weights))

  num_parts   = len(probabilities)
  partition_map = numpy.zeros((num_items,num_parts), dtype = 'bool')
  if probabilistic:
    c = numpy.cumsum(probabilities)
    r = rng.random_sample(num_items)
    partition_indices = numpy.searchsorted(c, r)
    for doc_index, part_index in enumerate(partition_indices):
      partition_map[doc_index, part_index] = True
  else:
    partition_sizes = numpy.floor(probabilities * num_items).astype(int)
    items_partitioned = partition_sizes.sum()
    gap = num_items - items_partitioned
    # Distribute the gap amongst the biggest partitions, adding one to each
    # This behaviour was deprecated as it does not behave well when partitions
    # all have the same size. The later partitions get favored by nature of the
    # argsort.
    # distribute_gap_to = numpy.argsort(partition_sizes) >= (num_parts - gap)
    # Randomly distribute it
    distribute_gap_to = numpy.concatenate(( numpy.ones(gap, dtype=bool), numpy.zeros(num_parts-gap, dtype=bool) ))
    rng.shuffle(distribute_gap_to)
    partition_sizes[distribute_gap_to] += 1
    assert partition_sizes.sum() == num_items
    indices = numpy.arange(num_items)
    rng.shuffle(indices)
    index        = 0
    for part_index, part_size in enumerate(partition_sizes):
      for i in xrange(part_size):
        doc_index = indices[index]
        partition_map[doc_index, part_index] = True
        index += 1
  return partition_map


def ceil_half(x):
  return x[:int(math.ceil(len(x) / 2.0))]
      
