"""Unit Briefer | Kabanov Andrew"""
# Модуль для генерации текста из n-грамм, используя тип nGrammBuilder_unit.NGrammsBuilder
# ===============================================================

# TODO:

# 26.11.2019
# +(T) Учёт спецсимволов и знаков препинаний, сейчас они «выброшены»
# 3:
# Вывести «плавную» формулу, учитывающая все параметры в совокупности!
# 2:
# Исключить повторения n-грамм ( создание нового дерева n-грамм, только если больше двух элементов? 04.12.2019 )
# 1:
# Вместо ранжированного списка tf-idf метрик для слов можно выбрать конкретные слова в виде запроса!
# Подтягивание неизвестных слов из википедии.
# 0:
# Использование больших словарей n-грамм

# оптимизация поиска подходящих n-грамм

# анализ вектора tf-idf предложения
# визуализация
# визуализация генерируемых предложений
# сравнение

# 03.12.2019
# TODO:
# вывод tf-idf top
# вывод "веса" предложения
# разбиение N-грамм
# вывод всех вариантов объединений с весом
# доделать леммизацию, учёт знаков, инициалов
# выводить данные по предложению (текстом без графики)

# построение графики предложений
# анализ графиков, сравнение с синтетическими предложениями
# решение по оптимизации
# построение отношений

# объединение n-грамм по нескольким вхождениям
# оптимизация объединения и поиска связанных n-грамм
# запрет на повторения n-грамм, в т.ч. одинаковых  n-грамм
# для этого испоолльзовать global tree?

# ========================================================================

# interface
#
# uses
import os
import sys
from enum import Enum

sys.path.append(os.path.abspath("../../units/"))

from kaTokenizer import TokenizerSymbolic as Tokenizer


# type

class Modes(Enum):
    """  """
    MINIMIZE_WORDS = 1

    """  """
    MINIMIZE_POOLS = 2

    """  """
    CENTER_POOLS = 3

    """ Мод для сайта """
    KY4 = 4


# const
ACTIVE_MODE = Modes.KY4

LOGGING = False  # True

""" Использовать ограничение на максимальную длинну предложения """
USE_WORDS_COUNT_LIMIT = True

"""
    Использовать ограничение на число объединений n-грамм,
    при значении True перестаёт действовать минимизация по длине предложения
"""
MINIMIZE_POOLS = (ACTIVE_MODE == Modes.MINIMIZE_POOLS) or (ACTIVE_MODE == Modes.CENTER_POOLS)

"""
Использование гибридной схемы построения предложения:
    начало и конец - минимизированы по словам
        (WORDS_LIMIT = True  MINIMIZE_POOLS = False),
    середина - минимизировання по объединениям и стремиться к рекомендуемой длинне предложения (BETTER_LENGTH)
        (WORDS_LIMIT = True  MINIMIZE_POOLS = True),
"""
USE_GYBRIDE = ACTIVE_MODE == Modes.CENTER_POOLS

""" Использовать принудительный выход по таймауту, в случае глубокой рекурсии """
USE_TIME_OUT = True

"""
Величина вызова операций, для принудительного выхода по таймауту, в том случае,
    если найдено хотя бы одно объединение
"""
LIGHT_TIME_OUT = 500000  # 0

"""
Величина вызова операций, для принудительного выхода по таймауту, в том случае,
    если даже не найдено объединение
"""
HARD_TIME_OUT = LIGHT_TIME_OUT * 3

""" Лимит слов в предложении """
WORDS_LIMIT = 25

""" Параметр оптимально величины предложения"""
BETTER_LENGTH = 7

""" Ограничение числа объединений (по умолчанию)"""
POOL_LIMIT = 9999

"""
classes:
    Briefer   //
"""


# implementation


class Briefer:
    def __init__(self, node_object, sentence_amount=10):
        self.minWay = WORDS_LIMIT
        self.min_pool = POOL_LIMIT
        self.better_way = []
        self.completed = 0
        self.node = node_object
        self.timer = 0
        self.mess = ''
        node_keys = list(node_object.tf_dict_sorted.keys())
        for i in range(sentence_amount):
            if len(node_keys) >= i * 2:
                self.build_full_sentence(node_keys[i * 2], node_keys[(i * 2) + 1])
        print(self.mess)

    def build_full_sentence(self, begin_word: str, end_word: str):
        sent_begin_tag = ('BEGINiSYSTEMiTAG'.lower()) + "i2"
        sent_end_tag = ('ENDiSYSTEMiTAG'.lower()) + "i2"

        sent_mid = self.build_sentences_by2lemms(begin_word, end_word)  # nodeKeys[0], nodeKeys[1])
        if ACTIVE_MODE == Modes.CENTER_POOLS:
            global MINIMIZE_POOLS
            MINIMIZE_POOLS = False

        if sent_mid is not None:
            last_word = sent_mid[-1:][0]
            sent_end = self.build_sentences_by2lemms(last_word, sent_end_tag, True)
            if sent_end is not None:
                last_word = sent_mid[:1][0]
                sent_begin = self.build_sentences_by2lemms(sent_begin_tag, last_word, True)
                if sent_begin is not None:
                    fusion_tag = [" "]  # [" _fusion_ "]
                    to_print_array = sent_begin[2:] + fusion_tag + sent_mid[1:] + fusion_tag + sent_end[1:-2]
                    to_print = " ".join(to_print_array)

                    self.mess = self.mess + " " + Tokenizer.repair_text(to_print)

        if ACTIVE_MODE == Modes.CENTER_POOLS:
            MINIMIZE_POOLS = True
        # USE_TIME_OUT = True

    def build_sentences_by2lemms(self, begin_word: str, end_word: str, by_words=False):
        self.minWay = WORDS_LIMIT
        self.min_pool = POOL_LIMIT
        self.better_way = []
        self.completed = 0
        self.timer = 0
        sentence = None
        searching_lemm = self.node.ng.word2lemm[end_word]
        if by_words:
            iterator = [self.node.all_ngramms[begin_word]]
        else:
            iterator = self.node.lemms2array_of_main_nodes.get(begin_word)
        for node in iterator:
            searched_ways = self.take_all_gramms4(node, searching_lemm, node.word, [node])
            if self.better_way:
                sentence = [sWay.word for sWay in self.better_way]
                self.completed = 0
        return sentence

    def take_all_gramms4(self, node, searching_lemm, history, way, pools=0):
        ways_list = []
        if USE_TIME_OUT:
            if ((self.timer > LIGHT_TIME_OUT) and (self.better_way != [])) or (self.timer > HARD_TIME_OUT):
                return ways_list
            else:
                self.timer += 1

        if MINIMIZE_POOLS and (pools > self.min_pool):
            return ways_list

        if len(way) > self.minWay:  # *2)):
            return ways_list

        for eachSubNodeKey in node.array_of_sub_ngramms:
            if LOGGING:
                print("%10s" % node.word + ' : ' + "%10s" % str(eachSubNodeKey) + '   :  ' + "%10s" % str(history))
            if len(way) == 1:
                self.completed += 100 / len(node.array_of_sub_ngramms)
            each_sub_node = node.array_of_sub_ngramms[eachSubNodeKey]
            new_way = way + [each_sub_node]
            new_history = str(history) + " " + str(each_sub_node.word)
            if each_sub_node.lemm == searching_lemm:
                ways_list.append(new_way)
                if MINIMIZE_POOLS:
                    if self.min_pool >= pools:
                        if ((BETTER_LENGTH - len(new_way)) ** 2) > ((BETTER_LENGTH - len(self.better_way)) ** 2):
                            self.min_pool = pools
                            self.better_way = new_way
                else:
                    if self.minWay > len(new_way):
                        self.minWay = len(new_way)
                        self.better_way = new_way
            else:
                if not (eachSubNodeKey in [step.word for step in way]):
                    searching_node = self.node.all_ngramms.get(eachSubNodeKey, None)
                    if searching_node is not None:
                        ways_list.extend(
                            self.take_all_gramms4(
                                searching_node, searching_lemm, new_history, (way + [searching_node]), pools + 1
                            )
                        )
                ways_list.extend(self.take_all_gramms4(each_sub_node, searching_lemm, new_history, new_way, pools))
        return ways_list
