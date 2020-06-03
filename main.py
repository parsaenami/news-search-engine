from __future__ import unicode_literals
import hazm
import parsivar
import re

from bs4 import BeautifulSoup

STOP_WORDS = hazm.stopwords_list()
SIGNS = {'.', '‫‪،‬‬', '!', '؟', '?', ':', '؛', '(', ')', '{', '}', '[', ']', '«', '»', '-', '/', '\\' '٪', '%', '"', "'",
         '،', '_', '=', '<', '>', '+', '@', '$', '^', '*', ',', ';', '&', '#', '٬', '`', '|', ',', 'ْ', 'ٌ', 'ٍ', 'ً', 'ُ', 'ِ', 'َ', 'ّ', }
SUFFIXES = {'ی', 'ای', 'ها', 'های', 'تر', 'تری',
            'ترین', 'گر', 'گری', 'ام', 'ات', 'اش', }
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
hazm.Normalizer()
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


def read_data():
    pass


def remove_emoji(input_text):
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', input_text)  # no emoji


def remove_bad_chars(text):
    for dest_char in BAD_CHARS.keys():
        for src_char in BAD_CHARS[dest_char]:
            text = text.replace(src_char, dest_char)


def remove_english(input_text):
    return re.sub(r'[A-Za-z0-9]+', '', input_text)


# TODO: try to handle it better
def correct_verbs(text):
    text = text.replace(' می ', ' می' + ZWNJ)
    text = text.replace(' نمی ', ' نمی' + ZWNJ)


def normalize(tokens):
    pass


def tokenize(text, mode):
    if mode == 1:
        pass
    elif mode == 2:
        pass
    else:
        print('Wrong tokenizing mode')


def stem(tokens):
    pass
