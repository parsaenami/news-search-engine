from __future__ import unicode_literals
import hazm
import parsivar
import re
import os

from bs4 import BeautifulSoup
import pandas as pd

from inverted_index import InvertedIndex

STOPWORDS = hazm.stopwords_list()
SIGNS = {'.', '‫‪،‬‬', '!', '؟', '?', ':', '؛', '(', ')', '{', '}', '[', ']', '«', '»', '-', '/', '\\' '٪', '%', '"', "'",
         '،', '_', '=', '<', '>', '+', '@', '$', '^', '*', ',', ';', '&', '#', '٬', '`', '|', ',', 'ْ', 'ٌ', 'ٍ', 'ً', 'ُ', 'ِ', 'َ', 'ّ', }
FARSI_DIGITS = list("۱۲۳۴۵۶۷۸۹۰")
ENGLISH_DIGITS = list("1234567890")
ARABIC_DIGITS = list("١٢٣٤٥٦٧٨٩٠")
ZWNJ = '\u200C'
ZWJ = '\u200D'
BAD_CHARS = {
    'ا': ['ا', 'إ', 'أ', 'ٱ'],
    'و': ['و', 'ؤ'],
    'ی': ['ی', 'ي', 'ئ'],
    'ک': ['ک', 'ك'],
    'ه': ['ه', 'ة', 'ۀ', 'هٔ'],
    ' ': SIGNS + FARSI_DIGITS + ENGLISH_DIGITS + ARABIC_DIGITS + [ZWJ],
}

index = InvertedIndex()
hazm.Normalizer()
stemmer = parsivar.FindStems()
lemmatizer = hazm.Lemmatizer()
tokenizer = hazm.WordTokenizer(
    replace_links=True,
    replace_hashtags=True,
    replace_emails=True,
    replace_IDs=True,
    join_verb_parts=True,
    replace_numbers=True,
)


# done ?
# test ?
def fetch_data():
    doc_id = 0
    data_files = os.listdir('news')

    for file in data_files:
        news_contents = pd.read_csv(file)['content']
        for nc in news_contents:
            pass


# done
# test
def remove_html_tags(html_input, remove_enters=False):
    output = BeautifulSoup(html_input, features="html.parser").text
    return output.replace('\n', ' ') if remove_enters else output


# done
# test ?
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


# done
# test ?
def remove_bad_chars(text):
    for dest_char in BAD_CHARS.keys():
        for src_char in BAD_CHARS[dest_char]:
            text = text.replace(src_char, dest_char)


# done
# test ?
def is_stopword(term):
    return term in STOPWORDS


# done
# test ?
def remove_english(text):
    return re.sub(r'[A-Za-z0-9]+', '', text)


# done
# test ?
def correct_verbs(term):
    # text = text.replace(' می ', ' می' + ZWNJ)
    # text = text.replace(' نمی ', ' نمی' + ZWNJ)
    term_stem = stemmer.convert_to_stem(term).split('&')
    return term_stem[0], term_stem[1]


# done ?
# test ?
def normalize(text, mode):
    if mode == 1:
        text = remove_html_tags(text, remove_enters=True)
        for _ in BAD_CHARS[' ']:
            text = text.replace(_, ' ')
        

    elif mode == 2:
        remove_bad_chars(text)

    else:
        print('Wrong tokenizing mode')


# done ?
# test ?
def tokenize(text: str, mode: int) -> list:
    tokens = set()

    if mode == 1:
        terms = text.split(' ')
        for term in terms:
            if not is_stopword(term):
                tokens.append(term)

        return
    elif mode == 2:
        terms = tokenizer.tokenize(text)
        for term in terms:
            pass

    else:
        print('Wrong tokenizing mode')


# done ?
# test ?
def stem(term):
    pass
