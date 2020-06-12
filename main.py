from __future__ import unicode_literals

import hazm
import parsivar
import re
import os
import sys
import json
from datetime import datetime

from typing import List
from bs4 import BeautifulSoup

import pandas as pd

from inverted_index import InvertedIndex

DATA_PATH = './news'
# DATA_PATH = './mock'

STOPWORDS_PATH = './preset/stopwords.txt'
SIGNS_PATH = './preset/signs.txt'
COMBINATIONS_PATH = './preset/combinations.txt'
BAD_CHARS_PATH = './preset/bad_characters.txt'
TEST_PATH = './preset/test.txt'

FARSI_DIGITS = list("۱۲۳۴۵۶۷۸۹۰")
ENGLISH_DIGITS = list("1234567890")
ARABIC_DIGITS = list("١٢٣٤٥٦٧٨٩٠")

ZWNJ = ['\u200C', '\u200F']
ZWJ = ['\u200D']

MISC_CHARS = ['\r', '\u00a0', '\xa0']

TEST_RES = {}

index = InvertedIndex()

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


def remove_duplicates(dup_list: list) -> list:
    """
    Removes duplicates from a list.
    """

    return list(set(dup_list))


def presets() -> tuple:
    """
    Fetches presets from project directory.

    Including:
    - Stop words
    - Common combinations
    - Bad characters
        - Numbers
        - Punctuations
        - Zero-width joiners
        - Arabic characters
    """

    swt = None
    st = None
    ct = None
    bct = None
    tt = None

    with open(STOPWORDS_PATH, encoding='utf-8') as swf:
        print("Getting stopwords... ", end='')
        swt = swf.read().split('\n')
        swt = remove_duplicates(swt)
        print("Done")

    with open(TEST_PATH, encoding='utf-8') as tf:
        print("Getting test words... ", end='')
        tt = tf.read().split('\n')
        tt = remove_duplicates(tt)
        print("Done")

    with open(SIGNS_PATH, encoding='utf-8') as sf:
        print("Getting signs... ", end='')
        st = sf.read().split('\n')
        st = remove_duplicates(st)
        print("Done")

    with open(COMBINATIONS_PATH, encoding='utf-8') as cf:
        print("Getting common combinations... ", end='')
        data_temp = {}
        data = cf.readlines()
        for d in data:
            combination = d.replace('\n', '').split(',')
            if not len(combination) < 1:
                data_temp[combination[0]] = combination

        ct = data_temp
        print("Done")

    with open(BAD_CHARS_PATH, encoding='utf-8') as bcf:
        print("Getting bad characters... ", end='')
        data_temp = {}
        data = bcf.readlines()
        for d in data:
            bad_char = d.replace('\n', '').split(',')
            if not len(bad_char) < 1:
                data_temp[bad_char[0]] = bad_char[1:]

        bct = data_temp
        print("Done")

    bct[' '] = list(st) + FARSI_DIGITS + \
        ENGLISH_DIGITS + ARABIC_DIGITS + ZWJ + MISC_CHARS
    bct[ZWNJ[0]] = ZWNJ[1:]

    return swt, st, ct, bct, tt


stuff = presets()
STOPWORDS = stuff[0]
SIGNS = stuff[1]
COMBINATIONS = stuff[2]
BAD_CHARS = stuff[3]
TEST = stuff[4]


def process_data(mode: int) -> None:
    """
    Fetches data to crawl and create inverted index.

    Data is stored in .csv files. 
    """

    print("Job started...")

    doc_id = 0
    data_files = os.listdir(DATA_PATH)

    for file in data_files:
        news_contents = pd.read_csv(f'{DATA_PATH}/{file}')['content']
        for nc in news_contents:
            if not doc_id % 1000:
                print(f":: Doc {doc_id} ::")
            tokens = my_tokenize(nc, mode=mode)
            # print(tokens)
            indexing(doc_id, tokens)
            doc_id += 1

    write_index_to_file(index.posting_lists, mode=mode)

    print("Job done")


def remove_html_tags(html_input: str, remove_enters=False) -> str:
    """
    Removes html tags from some piece of html code in string format.

    `remove_enters` replaces every `\\n` with space
    """

    output = BeautifulSoup(html_input, features="html.parser")
    for s in output.select('script'):
        s.extract()

    # print("Removing HTML tags... Done")

    return output.text.replace('\n', ' ') if remove_enters else output.text


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

    # print("Removing emojis... Done")

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

    for dest_char in BAD_CHARS.keys():
        for src_char in BAD_CHARS[dest_char]:
            text = text.replace(src_char, dest_char)

    # print("Removing bad characters... Done")

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
            text = text.replace(c, comb.replace(' ', '_'))

    # print("Finding common combinations... Done")

    return text


def remove_extra_zwnj(text: str) -> str:
    """
    Removes any extra ZWNJ.
    """

    while ZWNJ+ZWNJ in text:
        text = text.replace(ZWNJ+ZWNJ, ZWNJ)
    
    return text


def remove_english(text: str) -> str:
    """
    Removes any English character appeared in text.
    """

    # print("Removing English characters... Done")

    return re.sub(r'[A-Za-z0-9]+', '', text)


def correct_verbs(term: str, main_verb: str) -> str:
    """
    Finds the root of a verb and returns it.
    """

    term_stem = term.split('&')

    if term_stem[0] in main_verb:
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
    text = remove_bad_chars(text, mode=mode)
    text = remove_english(text)
    text = remove_emoji(text)
    text = remove_extra_zwnj(text)

    # print("Normalizing... Done")

    return text


def my_tokenize(text: str, mode: int) -> list:
    """
    Tokenizes the data of a document.

    - Normalizes the text
    - Splits tokens by space
    - Finds common combinations (mode 2 only)
    - Drops stop words
    - Stems each term (mode 2 only)

    `mode` determines how you want to tokenize your data. It can be 1 (simple) or 2 (advanced).

    This function returns a `list` of strings as tokens.
    """

    text = normalize(text, mode=mode)
    tokens = []

    if mode == 2:
        text = find_combination(text)

    terms = text.split(' ')
    for term in terms:
        if not is_stopword(term):
            tokens.append(term if mode == 1 else stem(term))

    # print("Tokenizing... Done")

    return tokens


def stem(term: str) -> str:
    """
    Finds the root of a word.
    """

    lemmatized = lemmatizer.lemmatize(term)
    stemmed = stemmer.convert_to_stem(lemmatized)

    if '&' in stemmed or '#' in stemmed:
        stemmed = stemmed.replace('#', '&')
        stemmed = correct_verbs(stemmed, term)

    if stemmed in TEST:
        TEST_RES.setdefault(stemmed, []).append(term)
        TEST_RES[stemmed] = remove_duplicates(TEST_RES[stemmed])

    return stemmed


def indexing(doc_id: int, tokens_list: list) -> None:
    """
    Creates inverted index and updates posting lists.

    This function updates an `InvertedIndex` object.
    """

    for pos, token in enumerate(tokens_list):
        index.add(token, doc_id, pos)


def write_index_to_file(index: dict, mode: int) -> None:
    """
    Writes the inverted index to a file for no reason.

    I just wanted to do this so I'd be able to see my inverted index.
    """

    if "" in index.keys():
        index.pop("")

    with open(f'index-{mode}.json', 'wb+') as jf:
        data_temp = json.dumps(index, ensure_ascii=False)
        buff_size = len(data_temp) // 10 ** 4

        for i in range(0, len(data_temp), buff_size):
            jf.write(data_temp[i:i + buff_size].encode("utf8"))

    with open(f'test-words-{mode}.json', 'wb+') as tf:
        tf.write(json.dumps(TEST_RES, ensure_ascii=False).encode("utf8"))

    with open(f'index-{mode}.txt', 'wb+') as f:
        for term in index:  # each term in index
            line = f"{term} -> "
            for doc in index[term]:  # posting lists of each term
                for pos in index[term][doc]:
                    line += f"({doc}, {pos}), "

            f.write(line[:-2].encode("utf8"))
            f.write(b'\n' + 40 * b'-' + b'\n')

    # print("Writing index to file... Done")


def dict_value_sort(x: dict) -> dict:
    """
    Sorts a dictionary by its values.
    """

    return {k: v for k, v in sorted(x.items(), key=lambda item: item[1])}


def dict_end_slice(x: dict, n: int) -> list:
    """
    Gives us the last `n` items of a dictionary.
    """

    return list(x.items())[n * -1:]


def pseudo_query(term: str, query_mode: int) -> list:
    """
    A simple query asking function.

    query modes:
    - `0`-> docs of a term
    - `1`-> docs + positions of a term
    - `2`-> doc frequency of a term
    - `3`-> term frequency
    - `4`-> n most frequent terms (docs only)
    - `5`-> m most frequent terms (docs + positions)
    """

    out = []
    if index.has_term(term) or query_mode in [4, 5, 6]:
        if query_mode == 0:  # docs of a term
            out = index.get_docs(term)

        elif query_mode == 1:  # docs + positions of a term
            for doc in index.get_docs(term):
                for pos in index.posting_lists[term][doc]:
                    out.append((doc, pos))

        elif query_mode == 2:  # doc frequency of a term
            out.append(index.doc_frequency(term))

        elif query_mode == 3:  # term frequency
            for doc in index.get_docs(term):
                out.append((doc, index.term_frequency(term, doc)))

            out = [sum([x[1] for x in out])]

        elif query_mode == 4:  # n most frequent terms (docs only)
            doc_freq = {}
            for t in index.posting_lists:
                doc_freq[t] = len(index.posting_lists[t])

            doc_freq = dict_value_sort(doc_freq)
            out = dict_end_slice(doc_freq, int(term))

        elif query_mode == 5:  # m most frequent terms (docs + positions)
            pos_freq = {}
            for t in index.posting_lists:
                freq = 0
                for doc in index.get_docs(t):
                    freq += len(index.posting_lists[t][doc])

                pos_freq[t] = freq

            pos_freq = dict_value_sort(pos_freq)
            out = dict_end_slice(pos_freq, int(term))

        elif query_mode == 6:
            print('Not implemented yet...')

        else:
            print('Wrong query mode, select again.')

    else:
        print(f"{term} doesn't exist :(")

    return out


def ask_query():
    """
    Gets queries from user and returns the result.
    """

    hint = "\n0 -> docs of a term\n"
    hint += "1 -> docs + positions of a term\n"
    hint += "2 -> doc frequency of a term\n"
    hint += "3 -> term frequency\n"
    hint += "4 -> n most frequent terms (docs only)\n"
    hint += "5 -> m most frequent terms (docs + positions)\n"
    hint += "6 -> Advanced query (not implemented yet)\n"
    hint += "# -> Exit\n"

    while True:
        q_mode = input(hint + '>>> ')
        if q_mode == '#':
            break
        else:
            q_mode = int(q_mode)

        q_term = input('Search: ')

        result = pseudo_query(q_term, q_mode)
        print(result)
        print(40 * '-')


if __name__ == "__main__":
    # MODE = int(sys.argv[1])
    MODE = 2
    want_load = input('Do you want to load an existing index file? (y/n): ')

    if want_load == 'y':
        path = input("Enter your json file path: ")
        start_time = datetime.now()
        index.load(path)
    else:
        start_time = datetime.now()
        process_data(MODE)

    end_time = datetime.now()
    print(f'\nProcess completed in {str(end_time - start_time)}')

    ask_query()
