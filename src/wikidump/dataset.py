"""
Code useful for preparing datasets from wikidump data
"""
import regexps

mediawiki_ignore_stringheads = '{}|=*#:'

def remove_mediawiki_syntax(text):
  "Remove non-content from a mediawiki page"
  text = regexps.redirect.sub('',text) # Remove redirects
  text = regexps.lang_link.sub('',text) # Remove language links
  text = regexps.template.sub('',text) # Remove templates TODO: Multi-line?
  text = regexps.intrawiki_link.sub(lambda x: x.group('anchor'), text) # Replace intrawiki links with anchor text
  text = re.sub('\n\n+', '\n\n', text) # Collapse multiple newlines
  return text

def paragraphs(text, minsize = 0):
  "Split text into paragraphs"
  return filter(lambda x: len(x) > minsize, text.split('\n\n'))
