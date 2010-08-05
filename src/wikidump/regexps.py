import re

import lang

mediawiki_ignore_stringheads = '{}|=*#:'

# Match the name of a dumpfile
dumpfile_name = re.compile(r'(.*?)wiki-')

intrawiki_link = re.compile(r"\[\[.*?\]\]")

lang_prefixes = '|'.join(lang.prefixes)
lang_link = re.compile(r"\[\[(?P<prefix>"+lang_prefixes+"):(?P<title>.+?)\]\]")

category_keywords = '|'.join(lang.category_identifier.values())
category_link = re.compile(r"\[\[(?P<title>("+category_keywords+"):(?P<category>.+?))\|.+?\]\]")
category_name = re.compile(r"(?P<keyword>("+category_keywords+")):(?P<category>.+)")
