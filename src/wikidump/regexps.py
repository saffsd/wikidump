import re

import lang

# Match the name of a dumpfile
dumpfile_name = re.compile(r'(?P<prefix>.*?)wiki-(?P<date>\d{8})-pages-articles.xml')

intrawiki_link = re.compile(r"\[\[(?P<target>.*?\|)?(?P<anchor>.*?)\]\]")

lang_prefixes = '|'.join(lang.prefixes)
lang_link = re.compile(r"\[\[(?P<prefix>"+lang_prefixes+"):(?P<title>.+?)\]\]")

category_keywords = '|'.join(lang.category_identifier.values())
category_link = re.compile(r"\[\[(?P<title>("+category_keywords+"):(?P<category>.+?))\|(.+?)\]\]")
category_name = re.compile(r"(?P<keyword>("+category_keywords+")):(?P<category>.+)")

redirect = re.compile(r"\#REDIRECT (?P<target>.*)")

template = re.compile(r"\{\{(?P<target>.*?)\}\}")

# Syntax-matching expressions developed for WikiTweets dataset
syntax = re.compile(r'\||\{|\}|==|\*|#|<|\(|:|;')
tripquote = re.compile(r"'''(?P<name>.*?)'''")
doubquote = re.compile(r"''(?P<name>.*?)''")
langref = re.compile(r'[\w-]+:')
assoc   = re.compile(r'\w+=')
