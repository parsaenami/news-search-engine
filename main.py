from __future__ import unicode_literals

import hazm
import parsivar
import re
import os

from typing import List
from bs4 import BeautifulSoup

import pandas as pd

from inverted_index import InvertedIndex


MODE = 1
COMBINATIONS = None
STOPWORDS = None
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
    ' ': list(SIGNS) + FARSI_DIGITS + ENGLISH_DIGITS + ARABIC_DIGITS + [ZWJ],
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


def presets() -> None:
    """
    Fetches presets from project directory.

    Including:
    - Stop words
    - Common combinations
    """

    with open('preset\stopwords.txt', encoding='utf-8') as swf:
        STOPWORDS = swf.read().split('\n')

    with open('preset\combinations.txt', encoding='utf-8') as cf:
        comb_temp = {}
        data = cf.readlines()
        for d in data:
            combination = d.replace('\n', '').split(',')
            if not len(combination) < 1:
                comb_temp[combination[0]] = combination

            COMBINATIONS = comb_temp


def fetch_data() -> None:
    """
    Fetches data to crawl and create inverted index.

    Data is stored in .csv files. 
    """

    doc_id = 0
    data_files = os.listdir('news')

    for file in data_files:
        news_contents = pd.read_csv(file)['content']
        for nc in news_contents:
            tokens = tokenize(nc, mode=MODE)
            indexing(doc_id, tokens)
            doc_id += 1


def remove_html_tags(html_input: str, remove_enters=False) -> str:
    """
    Removes html tags from some piece of html code in string format.

    `remove_enters` replaces every `\\n` with space
    """

    output = BeautifulSoup(html_input, features="html.parser").text
    return output.replace('\n', ' ') if remove_enters else output


def remove_emoji(input_text: str) -> str:
    """
    Removes any emojis appeared in text.
    """

    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', input_text)  # no emoji


def remove_bad_chars(text: str, mode: int) -> str:
    """
    Removes bad characters like:
    - Punctuations
    - Numbers
    - Zero-width joiners
    - Arabic characters

    `mode` determines how you want to tokenize your data. It can be 1 (simple) or 2 (advanced).
    """

    if mode == 1:
        for dest_char in BAD_CHARS.keys():
            for src_char in BAD_CHARS[dest_char]:
                text = text.replace(src_char, dest_char)

    elif mode == 2:
        for _ in BAD_CHARS[' ']:
            text = text.replace(_, ' ')

    else:
        print('Wrong tokenizing mode')

    return text


def is_stopword(term: str) -> bool:
    """
    Tells if a word is a stop word or not.
    """

    return term in STOPWORDS


def find_combination(text: str) -> str:
    """
    Finds some of most common combinations in Persian and prevent tokenizer to separate them.
    """

    for comb in COMBINATIONS.keys():
        for c in COMBINATIONS[comb]:
            text.replace(c, comb.replace(' ', '_'))

    return text


def remove_english(text: str) -> str:
    """
    Removes any English character appeared in text.
    """

    return re.sub(r'[A-Za-z0-9]+', '', text)


def correct_verbs(term: str) -> str:
    """
    Finds the root of a verb and returns it.
    """

    # text = text.replace(' می ', ' می' + ZWNJ)
    # text = text.replace(' نمی ', ' نمی' + ZWNJ)
    term_stem = term.split('&')

    if term_stem[0] in term:
        return term_stem[0]
    else:
        return term_stem[1]


def normalize(text: str, mode: int) -> str:
    """
    Normalizes a text. 
    1. removes html tags
    2. removes bad characters
    3. removes English characters (mode 2 only)
    4. removes emojis (mode 2 only)

    `mode` determines how you want to tokenize your data. It can be 1 (simple) or 2 (advanced).
    """

    text = remove_html_tags(text, remove_enters=True)
    remove_bad_chars(text, mode=mode)

    if mode == 2:
        text = remove_english(text)
        text = remove_emoji(text)

    return text


def tokenize(text: str, mode: int) -> List[str]:
    """
    Tokenizes the data of a document.

    - mode 1
    1. Normalizes the text
    2. Splits tokens by space
    3. Drops stop words

    - mode 2
    1. Normalizes the text
    2. Finds common combinations
    3. Drops stop words
    4. Stems each term
    
    `mode` determines how you want to tokenize your data. It can be 1 (simple) or 2 (advanced).

    This function returns a `list` of strings as tokens.
    """

    text = normalize(text, mode=mode)
    tokens = set()

    if mode == 1:
        terms = text.split(' ')
        for term in terms:
            if not is_stopword(term):
                tokens.add(term)

    elif mode == 2:
        text = find_combination(text)
        terms = tokenizer.tokenize(text)
        for term in terms:
            if not is_stopword(term):
                tokens.add(stem(term))

    else:
        print('Wrong tokenizing mode')

    return list(tokens)


def stem(term: str) -> str:
    """
    Finds the root of a word.
    """

    lemmatized = lemmatizer.lemmatize(term)
    stemmed = stemmer.convert_to_stem(lemmatized)

    if '&' in stemmed or '#' in stemmed:
        stemmed = stemmed.replace('#', '&')
        stemmed = correct_verbs(stemmed)

    return stemmed


def indexing(doc_id: int, tokens_list: list) -> None:
    """
    Creates inverted index and updates posting lists.

    This function updates an `InvertedIndex` object.
    """

    for pos, token in enumerate(tokens_list):
        index.add(token, doc_id, pos)
