from common.decorators import shelved
from utils import page_parser, dumpSize
from time import time
import os
from utils import all_prefixes, raw_doc_lengths
from doclength_threshold import docs_under_thresh
import numpy as n
from matplotlib.font_manager import FontProperties
import pylab as p
import operator
from utils import dumpSize

html_colors = [ 'aqua'
              , 'red'
              , 'blue'
              , 'fuchsia'
              , 'teal'
              , 'maroon'
              , 'purple'
              , 'navy'
              , 'green'
              , 'olive'
              , 'yellow'
              , 'lime'
              , 'gray'
              , 'silver'
              ]

def produce_graphs():
  length_stats_chart('output/wikipedia_doclength_stats_median.png', all_prefixes,1)
  length_stats_chart('output/wikipedia_doclength_stats_mean.png', all_prefixes,2)
  length_stats_chart('output/wikipedia_doclength_stats_sd.png', all_prefixes,3)
  #wiki_sizes_chart('output/wiki_size_chart.png', all_prefixes)  
  #wiki_sizes_chart('output/wiki_size_chart_10000_upper.png', all_prefixes, 10000)  
  #wiki_sizes_chart('output/wiki_size_chart_100000_upper.png', all_prefixes, 100000)  
  #wiki_proportions_chart('output/wiki_doclen_proportions.png', all_prefixes)

def overall_collection_stats():
  doc_lengths = []
  for prefix in all_prefixes:
    doc_lengths += raw_doc_lengths(prefix).values()
  print "All documents length mean: %.2f" % n.mean(doc_lengths)
  print "All documents length std: %.2f" % n.std(doc_lengths)
  print "All documents length median: %.2f" % n.median(doc_lengths)
  medlist, meanlist, stdlist = zip(*map(length_stats,all_prefixes))
  print "Mean of means: %.2f" % n.mean(meanlist)
  print "Mean of std: %.2f" % n.mean(stdlist)
  print "Mean of median: %.2f" % n.mean(medlist)

@shelved("length_stats")
def length_stats(prefix):
  doc_lengths = raw_doc_lengths(prefix).values()
  median = n.median(doc_lengths)
  mean   = n.mean(doc_lengths)
  std    = n.std(doc_lengths)
  return median, mean, std
    
def rounded_interval(min, max, points, divs=1):
  exact = (max - min) / points
  from math import log
  return (10 ** round(log(exact*divs,10))) / divs

def wiki_proportions_chart(path, prefixes):
  prefixes, sizes = zip(*sorted( [(pr, dumpSize(pr)) for pr in prefixes]
                               , key = operator.itemgetter(1)
                               )
                       )

  blockSize = 5 
  ind = p.arange(0, blockSize*len(prefixes), blockSize) # y location for groups
  height = 4 # bar height 

  #colors = ['g','r','c','m','y']
  thresholds = [5000, 2000,1000,500,200,100,50,20,10]
  colors = [str(float(i+1) / (len(thresholds)+1)) for i in xrange(len(thresholds))]
  colors.reverse()

  p.clf()
  """
  overall = p.barh( ind 
                  , [1.0] * len(ind) 
                  , height
                  , color = 'b'
                  , linewidth = 0
                  , align='center'
                  )
  """
  subbars = []
  for i, thresh in enumerate(thresholds) :
    subbars.append( p.barh( ind
                          , [ float(docs_under_thresh(pr, thresh)) / dumpSize(pr) for pr in prefixes]
                          , height
                          , color = colors[ i % len(colors) ] 
                          , linewidth = 0
                          , align='center'
                          )
                  )
  
  p.ylim(-height, len(prefixes) * blockSize)
  p.xlim(0, 1)
  yfontprop = FontProperties(size=4)
  xfontprop = FontProperties(size=4)
  p.xlabel('Proportion')
  p.ylabel('Language Code')
  p.title('Proportion of Documents Under Threshold')
  p.yticks(ind, prefixes, fontproperties = yfontprop)
  xmin, xmax = p.xlim()
  xtick_interval         = 0.1 
  p.xticks( p.arange(xmin,xmax,xtick_interval),fontproperties = xfontprop)
  p.gca().xaxis.grid(linestyle = '-', linewidth=0.15)
  p.gca().yaxis.tick_left()
  p.savefig(path, dpi=300)
  p.close()
  p.clf()
  
  
def wiki_sizes_chart(path, prefixes, upperlimit = None ):
  prefixes, sizes = zip(*sorted( [(pr, dumpSize(pr)) for pr in prefixes]
                               , key = operator.itemgetter(1)
                               )
                       )

  blockSize = 5 
  ind = p.arange(0, blockSize*len(prefixes), blockSize) # y location for groups
  height = 4 # bar height 

  #colors = ['g','r','c','m','y']
  colors = html_colors

  thresholds = [5000, 2000,1000,500,200,100,50,20,10]
  #colors = [str(float(i+1) / (len(thresholds)+1)) for i in xrange(len(thresholds))]
  #colors.reverse()

  overall = p.barh( ind 
                  , sizes
                  , height
                  , color = 'b'
                  , linewidth = 0
                  , align='center'
                  )
  subbars = []
  for i, thresh in enumerate(thresholds) :
    subbars.append( p.barh( ind
                          , [ docs_under_thresh(pr, thresh) for pr in prefixes]
                          , height
                          , color = colors[ i % len(colors) ] 
                          , linewidth = 0
                          , align='center'
                          )
                  )
  
  p.ylim(-height, len(prefixes) * blockSize)
  if upperlimit:
    p.xlim(0, upperlimit)
  yfontprop = FontProperties(size=4)
  xfontprop = FontProperties(size=4)
  p.xlabel('Documents')
  p.ylabel('Language Code')
  p.title('Number of Documents Under Threshold')
  p.yticks(ind, prefixes, fontproperties = yfontprop)
  xmin, xmax = p.xlim()
  xtick_interval         = rounded_interval(xmin, xmax, 20, 2) 
  p.xticks( p.arange(xmin,xmax,xtick_interval),fontproperties = xfontprop)
  p.gca().xaxis.grid(linestyle = '-', linewidth=0.15)
  p.gca().yaxis.tick_left()
  p.legend( [ b[0] for b in subbars]
          , map(str,thresholds)
          , prop = xfontprop
          , loc = 'lower right' 
          )


  p.savefig(path, dpi=300)
  p.close()
  p.clf()
  

def length_stats_chart(path, prefixes, sortby=1):
  stats = []
  for prefix in prefixes:
    med, m,s = length_stats(prefix)
    stats.append((prefix,med,m,s))

  stats.sort(key=operator.itemgetter(sortby))
  prefixes, med_list, mean_list, std_list = zip(*stats)

  blockSize = 8 
  ind = p.arange(0, blockSize*len(prefixes), blockSize) # y location for groups
  height = 3 # bar height 

  p3 = p.barh(ind, std_list, 2   * height, color = 'b', linewidth = 0)
  p2 = p.barh(ind, med_list, height, color = 'g', linewidth = 0)
  p1 = p.barh(ind+height, mean_list, height, color = 'r', linewidth = 0)
  
  p.ylim(-height, len(prefixes) * blockSize)
  yfontprop = FontProperties(size=4)
  xfontprop = FontProperties(size='smaller')
  p.xlabel('Unicode Codepoints')
  p.ylabel('Language Code')
  p.title('Descriptive Statistics for Document Lengths')
  p.gca().yaxis.tick_left()
  p.yticks(ind+height, prefixes, fontproperties = yfontprop)
  xmin, xmax = p.xlim()
  p.xticks( p.arange(xmin,xmax,1000),fontproperties = xfontprop)
  p.gca().xaxis.grid(linestyle = '-', linewidth=0.15)
  p.legend((p1[0], p2[0], p3[0]), ('Mean','Median','Standard Deviation'), prop = xfontprop, loc = 'lower right' )

  p.savefig(path, dpi=300)
  p.close()
  p.clf()

  

def doclength_histogram(path, prefix):
  values = p.array(raw_doc_lengths(prefix).values())
  num_bins = 1000
  bin_upper_limit = p.mean(values) + 3 * p.std(values)
  print "UL: "+ str(bin_upper_limit)
  bins = p.array(range(1,1001)) * (bin_upper_limit/1000.0)
  p.hist(values, bins)
  p.xlabel('Document size (unicode codepoints)')
  p.ylabel('Number of documents')
  p.title('Document Size Histogram for %s' % prefix)
  p.savefig(path, dpi=72)
  p.close()
  
def all_prefix_length_histograms(path):
  for prefix in all_prefixes:
    outpath = os.path.join(path, "%s_doclength_hist.png"%prefix)
    doclength_histogram(outpath, prefix)
