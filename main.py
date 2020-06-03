import hazm
import re

from bs4 import BeautifulSoup

STOP_WORDS = hazm.stopwords_list()
SIGNS = ['.', '‫‪،‬‬', '!', '؟', '?', ':', '؛', '(', ')', '{', '}', '[', ']', '«', '»', '-', '/', '٪', '%', '"', "'",
         '،', '_', '=', '<', '>', '+', '@', '*', ',', ';', '&', '#', '٬', '`', '|', ',', 'ْ', 'ٌ', 'ٍ', 'ً', 'ُ', 'ِ', 'َ', 'ّ']
DIGITS = list("1234567890۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩")
ZWNJ = '\u200C'
ZWJ = '\u200D'
BAD_CHARS = {
    'ا': ['ا', 'إ', 'أ', 'ٱ'],
    'و': ['و', 'ؤ'],
    'ی': ['ی', 'ي', 'ئ'],
    'ک': ['ک', 'ك'],
    'ه': ['ه', 'ة', 'ۀ', 'هٔ'],
    ' ': SIGNS + DIGITS + [ZWJ],
}

stemmer = hazm.Stemmer()
lemmatizer = hazm.Lemmatizer()
tokenizer = hazm.WordTokenizer(
    replace_links=True,
    replace_hashtags=True,
    replace_emails=True,
    replace_IDs=True,
    join_verb_parts=True,
    replace_numbers=True,
)



