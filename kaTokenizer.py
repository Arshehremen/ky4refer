"""Unit Tokenizer Kabanov Andrew"""
# Модуль для токенизации, лемматизации, выделения предложений или абзацев.

# interface

# uses
from nltk import regexp_tokenize  # just change to re
import pymorphy2

# type

"""
classes:
    Tokenizer            //
    TokenizerSymbolic   //
"""


# implementation


# класс для выделения лемм
class Tokenizer:
    @staticmethod
    def word_tokenize(text: str, contains_html=False):
        if contains_html:
            sent_tokenizer_words = (
                lambda s: regexp_tokenize(s, r'<[^>]*?>|[\.\,:][^\w]|\.$|[^\w$\,\.\'%:-<>]+|;', gaps=True)
            )
        else:
            # TODO: переделать
            sent_tokenizer_words = (
                lambda s: regexp_tokenize(s, r'<[^>]*?>|[\.\,:][^\w]|\.$|[^\w$\,\.\'%:-<>]+|;', gaps=True)
            )
        return sent_tokenizer_words(text)

    @staticmethod
    def to_lemms(words_array):
        morph = pymorphy2.MorphAnalyzer()
        return [morph.parse(x)[0].normal_form for x in words_array]

    @staticmethod
    def count_words(words_array: list) -> dict:
        ss = dict.fromkeys(words_array, 0)
        for word in words_array:
            ss[word] = ss[word] + 1
        return ss

    @staticmethod
    def paragraphs_tokenize(text):
        sent_paragraphs_tokenize = (lambda s: regexp_tokenize(s, r'\n', gaps=True))
        paragraphs_array = sent_paragraphs_tokenize(text)
        return [value for value in paragraphs_array if (value.strip() != '')]

    @staticmethod
    def sentences_tokenize(text):
        sent_sentences_tokenize = (
            lambda s: regexp_tokenize(
                s, r'[\n]|([\dA-ZА-Я]+[^\n\.\?\!]*[\w]{2,}[\s]?[\.\?\!]+\s+[^\dA-ZА-Я\n]*)', gaps=True
            )
        )
        sentences_array = sent_sentences_tokenize(text)
        end = False

        def if_end(e_value):
            nonlocal end
            if (e_value == 'Источники') or (e_value == 'Источник —'):
                end = True
            return end

        sentences_array = [value.strip() for value in sentences_array
                           if (value.strip() != '') and
                           (value.strip() != '\n') and
                           (value.strip() != '\r') and
                           (value.strip() != '\n\r') and
                           (value.strip() != '«') and
                           (value.strip() != '»') and
                           (not if_end(value.strip()))]
        return sentences_array

    @staticmethod
    def repair_text(text: str) -> str:
        return text

class TokenizerSymbolic(Tokenizer):

    @staticmethod
    def replace_tags(original_text):

        tagged_text = original_text.replace(' итал.', ' итальянский')
        tagged_text = tagged_text.replace(' ум.', ' умиротворённый')
        tagged_text = tagged_text.replace('(ум.', '(умиротворённый')
        tagged_text = tagged_text.replace(' фр.', ' французское')
        tagged_text = tagged_text.replace('(фр.', '(французское')
        tagged_text = tagged_text.replace(' англ..', ' английское')
        tagged_text = tagged_text.replace('(англ..', '(английское')
        tagged_text = tagged_text.replace(' г.', ' год')
        tagged_text = tagged_text.replace(';', ' точкаСЗапятой ')
        tagged_text = tagged_text.replace(' чел.', ' челтчкскр')
        tagged_text = tagged_text.replace('===', '==')
        tagged_text = tagged_text.replace('==', '')
        array_big_chars = list('QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ')
        for big_char in array_big_chars:
            tagged_text = tagged_text.replace(' ' + big_char + '.', ' инициалИмени' + big_char)
        stop_tags = [
            '== Ссылки ==',
            '== Литература ==',
            '== Примечания =='
        ]
        for stop_tag in stop_tags:
            have_links = tagged_text.find(stop_tag)
            if have_links > 0:
                tagged_text = tagged_text[:have_links]

        return tagged_text

    @staticmethod
    def word_tokenize(text_to_split: str):
        text = TokenizerSymbolic.replace_tags(text_to_split)
        words_array = []
        cur_word = []

        def add_word(fill_list: list, word: list):
            cur_word_str = ''.join(word).strip()
            if cur_word_str != '':
                fill_list.append(cur_word_str)

        for char in text:
            if char.strip() == '':
                add_word(words_array, cur_word)
                cur_word.clear()
            elif char in list('~!@#№$%^&*()-_=+\\|/\'":;?.,<>«»{}[]'):
                add_word(words_array, cur_word)
                add_word(words_array, [char])
                cur_word.clear()
            else:
                cur_word.append(char)
        add_word(words_array, cur_word)
        return words_array

    @staticmethod
    def sentences_tokenize(text_to_split: str):
        text = TokenizerSymbolic.replace_tags(text_to_split)
        sentence_end_symvols = list('.!?\n')
        minimum_length_of_sentence = 3
        symvols_count = 0
        sentences_array = []  # sent_sentencesTokenize(text)
        filling_sentence = []
        for char in text:
            if char != '\n':
                filling_sentence.append(char)
                symvols_count += 1
            if char.strip() in sentence_end_symvols:
                if symvols_count > minimum_length_of_sentence:
                    sentences_array.append("".join(filling_sentence))
                    filling_sentence = []
                symvols_count = 0
        return sentences_array

    @staticmethod
    def repair_text(text: str) -> str:
        repaired_text = text
        array_big_chars = list('QWERTYUIOPASDFGHJKLZXCVBNMЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ'.lower())
        for big_char in array_big_chars:
            repaired_text = repaired_text.replace(' инициалИмени' + big_char, ' ' + big_char.upper() + '.')

        repaired_text = repaired_text.replace('   ', ' ')
        repaired_text = repaired_text.replace('  ', ' ')

        repaired_text = repaired_text.replace('умиротворённый', 'ум.')
        repaired_text = repaired_text.replace('английское', 'англ..')
        repaired_text = repaired_text.replace('итальянский', 'итал.')
        repaired_text = repaired_text.replace('французское', 'фр.')
        repaired_text = repaired_text.replace(' год ', ' г. ')
        repaired_text = repaired_text.replace(' челтчкскр', ' чел.')
        repaired_text = repaired_text.replace(' точкасзапятой ', '; ')
        repaired_text = repaired_text.replace(' ;', ';')
        repaired_text = repaired_text.replace(' :', ':')
        repaired_text = repaired_text.replace(' .', '.')
        repaired_text = repaired_text.replace(' ,', ',')
        repaired_text = repaired_text.replace(' !', '!')
        repaired_text = repaired_text.replace(' ?', '?')
        repaired_text = repaired_text.replace(' )', ')')
        repaired_text = repaired_text.replace('( ', '(')
        repaired_text = repaired_text.replace(' »', '»')
        repaired_text = repaired_text.replace('« ', '«')
        repaired_text = repaired_text[:1].upper() + repaired_text[1:]
        return repaired_text

def test():
    from kaWikipedia import WikipediaReader
    s = WikipediaReader().take_rnd()
    t = s.take_random_pages()
    tt = t.texts[0]
    print(tt)
    TokenizerSymbolic.word_tokenize(tt)

# test()
