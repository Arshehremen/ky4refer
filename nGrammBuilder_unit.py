# coding=utf-8
"""Unit N-Gramm builder | Kabanov Andrew"""
# Модуль для составления деревьев n-грамм из текста и выделения наиболее значимых слов

# interface

# uses

import os
import sys

import briefer_unit as briefer

sys.path.append(os.path.abspath("../../units/"))

from kaTokenizer import TokenizerSymbolic as Tokenizer

# type

# const
LOGGING = False  # True
TESTING = False  # True
WORDS_FOR_TEST = 50
USE_LOWER = True
MATH_TFIDF = True
DOCUMENTS_COUNT_TAG = u'howMuchDocumentsReadedForAllTimeTrickNumberOne'
DEFAULT_DF = 7  # это то что делать с неизвестными словам в тексте:
# 1 - считать что у слова такой же вес как у самых редких слов, или
# 3 - считать что такое слово не самое редкое и встречалось уже 3 раза, синтетически уменьшая его значимость
# 7 - пересчитанное значение от 19.12.2019

if MATH_TFIDF:
    import math

"""
classes:
    NG                //
    NGrammObject     //
    NGrammsBuilder  //
"""


# implementation

class NG:
    def __init__(self):
        self.word2lemm = {}
        self.dict_df = {}
        self.dict_tf = {}
        if os.path.isfile('df.csv'):
            df_file = open("df.csv", "r", encoding='utf-8')
            df_lines = df_file.readlines()
            for line in df_lines:
                td = line.split(';')
                self.dict_df[td[0]] = int(td[1].strip())
            df_file.close()

    def DF(self, word: str) -> int:
        lemm_of_word = self.word2lemm.setdefault(word, Tokenizer.to_lemms([word])[0])
        df = self.dict_df.setdefault(lemm_of_word, 0)
        if df == 0:
            self.dict_df[lemm_of_word] = DEFAULT_DF
            df = DEFAULT_DF
            if LOGGING and (word != DOCUMENTS_COUNT_TAG):
                print('special word:   ', word)
        return df

    def math_tf(self, words, exceptions):
        lemms = Tokenizer.to_lemms(words)
        counted_lemms = Tokenizer.count_words(lemms)
        words_tf = {}
        doc_count = self.dict_df[DOCUMENTS_COUNT_TAG]
        if LOGGING:
            print('doc count', doc_count)
        for i in range(len(words)):
            self.word2lemm[words[i]] = lemms[i]
        exceptions_lemms = [self.word2lemm[word] for word in exceptions]

        for word in counted_lemms:
            if word in exceptions_lemms:
                words_tf[word] = -10
            else:
                if MATH_TFIDF:
                    idf = math.log10(doc_count / self.DF(word))
                else:
                    idf = 1
                if LOGGING:
                    print("%20s" % word + '   │  ' + "%20s" % str(idf) + '   │   ' + "%10s" % str(counted_lemms[word]))
                words_tf[word] = idf * counted_lemms[word]
        return words_tf

    def probability(self, words_array: list):
        def mult(array_of_integer: list) -> int:
            multiplier = 1
            for intValue in array_of_integer:
                multiplier = multiplier * intValue
            return multiplier

        return len(words_array) / (mult([self.DF(word) for word in words_array]))


class NGrammObject:
    def __init__(self, word: str, lemm: str, owner=None):
        self.owner = owner
        self.lemm = lemm
        self.word = word
        self.stop_weight = int(0)
        self.array_of_sub_ngramms = {}  # dict str -> NGrammObject

    def add_word(self, word: str, lemm: str):
        word_object = self.array_of_sub_ngramms.setdefault(
            lemm,
            NGrammObject(word, lemm, self)
        )  # serach on inner dict first
        word_object.stop_weight += 1
        return word_object

    def __str__(self):
        ss = self.owner
        tabs = ''
        while ss is not None:
            tabs = tabs + '\t'
            ss = ss.owner
        return ' : ' + str(self.stop_weight) + '\n' + tabs + str(self.array_of_sub_ngramms) + ' \n'

    __repr__ = __str__


class NGrammsBuilder:
    def __init__(self, text2brief: str, sent_count2output: int):
        self.ng = NG()
        self.text = text2brief
        self.lemms2array_of_main_nodes = {}

        self.sentences = Tokenizer.sentences_tokenize(self.text)
        sent_begin_tag = 'BEGINiSYSTEMiTAG'.lower()
        sent_end_tag = 'ENDiSYSTEMiTAG'.lower()
        self.text_with_begin_end = sent_begin_tag + "i2 " + \
                                   sent_begin_tag + "i1 " + \
                                   (
                                       (" " + sent_end_tag + "i1 " + sent_end_tag +
                                        "i2 " + sent_begin_tag + "i2 " + sent_begin_tag + "i1 ").join(self.sentences)
                                   ) + \
                                   " " + sent_end_tag + \
                                   "i1 " + sent_end_tag + "i2"

        if LOGGING:
            print('text after add begin and end tags ', self.text_with_begin_end)
        self.words = Tokenizer.word_tokenize(self.text_with_begin_end)
        if TESTING:
            self.words = self.words[:WORDS_FOR_TEST]
        exceptions = [
            sent_end_tag + "i1",
            sent_end_tag + "i2",
            sent_begin_tag + "i2",
            sent_begin_tag + "i1"
        ]  # , DOCUMENTS_COUNT_TAG]
        if USE_LOWER:
            self.words = [word.lower() for word in self.words]
        self.tf_dict = self.ng.math_tf(self.words, exceptions)
        self.tf_dict_sorted = dict(sorted(self.tf_dict.items(), key=lambda word: word[1], reverse=True))
        if LOGGING:
            print('Sorted words by TD-IFD metric: ', self.tf_dict_sorted)

        self.all_ngramms = {}
        array_of_filling_ngramms = []
        for word in self.words:
            lemm = self.ng.word2lemm[word]
            if LOGGING:
                print('Word to brief ' + "%20s" % word + ' : as lemm to brief : ' + "%20s" % lemm)
            array_of_filling_ngramms = [fillingNGramm.add_word(word, lemm) for fillingNGramm in
                                        array_of_filling_ngramms]
            new_node = self.add_new_node(word, lemm)
            array_of_filling_ngramms.append(new_node)
            if word == sent_end_tag + 'i2':
                array_of_filling_ngramms = []

    def add_new_node(self, word: str, lemm: str):
        new_node = self.all_ngramms.get(word, None)
        if new_node is None:
            new_node = NGrammObject(word, lemm)
            self.all_ngramms[word] = new_node
            nodes_array4lemm = self.lemms2array_of_main_nodes.setdefault(lemm, [])
            nodes_array4lemm.append(new_node)
        return new_node

    def __str__(self):
        return '\n\n' + str(self.all_ngramms)


