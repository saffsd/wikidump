import os 
import re

re_link = re.compile(r"\[\[(.*?\|)?(?P<link>.*?)\]\]")
re_cat = re.compile(r"\{\{(.*?)\}\}")
re_lang_link = re.compile(r"\[\[(?P<prefix>[-a-z]*):(?P<title>.+)\]\]")
re_redirect = re.compile(r"\#REDIRECT .*")

def clean(text):
  text = re_redirect.sub('',text) # Remove redirects
  text = re_lang_link.sub('',text) # Remove language links
  text = re_cat.sub('',text) # Remove stuff in curly braces. Categories??
  text = re_link.sub(lambda x: x.group('link'), text) # Replace intrawiki links with anchor text
  text = re.sub('\n\n+', '\n\n', text) # Collapse multiple newlines
  return text

def paragraphs(text, minsize = 0):
  return filter(lambda x: len(x) > minsize, text.split('\n\n'))
