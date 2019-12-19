"""Unit DF counter | Kabanov Andrew"""
# подсчет подокументной частоты слов модели:
#    составление статистики df для термов
#    ведение счетчика документов

# interface

# uses

import os
import sys
import time

sys.path.append(os.path.abspath("../../units/"))

from kaWikipedia import WikipediaReader  # as WikipediaReader
from kaTokenizer import TokenizerSymbolic as Tokenizer

# type

# const
DOCUMENTS_PER_QUERY = 100
LOGGING = False  # True
SPECIAL_WORD_DOCUMENTS_COUNT = 'howMuchDocumentsReadedForAllTimeTrickNumberOne'
FILE_NAME_TO_SAVE_DF = 'df.csv'

"""
classes:
    DFCounter   //
    Counter    //
"""


# implementation


class DFCounter:
    def count(array_of_array_of_words) -> dict:
        df = {}
        for eachArrayOfWords in array_of_array_of_words:
            for eachWord in eachArrayOfWords:
                df[eachWord] = df.get(eachWord, 0) + 1
        df = dict(sorted(df.items(), key=lambda word: word[1], reverse=True))
        df[SPECIAL_WORD_DOCUMENTS_COUNT] = len(array_of_array_of_words)
        return df

    def saveDFToFile(df):
        old_df = {}
        if os.path.isfile(FILE_NAME_TO_SAVE_DF):
            df_file = open(FILE_NAME_TO_SAVE_DF, "r")
            df_lines = df_file.readlines()
            for line in df_lines:
                td = line.split(';')
                old_df[td[0]] = int(td[1].strip())
            if LOGGING:
                print('old df from file:\n', old_df)
            df_file.close()
        df_file = open(FILE_NAME_TO_SAVE_DF, "w+")
        if LOGGING:
            print('merge with old file:')
        new_df = {}
        for eachWord in set(list(df.keys()) + list(old_df.keys())):
            new_df[eachWord] = df.get(eachWord, 0) + old_df.get(eachWord, 0)
        new_df = dict(sorted(new_df.items(), key=lambda word: word[1], reverse=True))
        print_only = 20
        for eachWord in new_df:
            try:
                line_for_write = eachWord + ';' + str(new_df[eachWord])
                if print_only != 1:
                    print(line_for_write)
                if print_only > 1:
                    print_only += -1
                df_file.write(line_for_write + '\n')
            except:
                print('can not write ', eachWord)
        df_file.close()
        return new_df


class Counter:
    def __init__(self):
        self.texts = WikipediaReader().takeRnd(DOCUMENTS_PER_QUERY).takeRandomPages().texts
        if LOGGING:
            print(self.texts)
        self.wordsArrays = [list(set(Tokenizer.toLemms(Tokenizer.wordTokenize(eachText)))) for eachText in self.texts]
        self.df = DFCounter.count(self.wordsArrays)
        if LOGGING:
            print(self.df)
        DFCounter.saveDFToFile(self.df)


def longCounter():
    for i in range(10000):
        print('\niteration : ' + str(i) + ' : ')
        time.sleep(1)
        Counter()


def count():
    Counter()
