"""
Info for statistic:
a. список файлов и папок,
b. общее количество файлов,
c. самые частые/редкие слова,
d. средний размер слова,
e. статистика по согласным и гласным,
f. статистика по слогам (*)
"""
import re
from collections import Counter
from itertools import chain
import string

import pyphen


def tokenize(file_content):
    pattern = re.compile('[a-z]|[а-яё]')
    word_buffer = ''
    for line in file_content:
        for symbol in line:
            if pattern.match(symbol.lower()):
                word_buffer += symbol.lower()
            else:
                if word_buffer:
                    yield WordToken(value=word_buffer.lower(),
                                    counted_letters=len(word_buffer))
                    word_buffer = ''
    if word_buffer != '':
        yield WordToken(value=word_buffer.lower(),
                        counted_letters=len(word_buffer))


class WordToken:

    def __init__(self, value, counted_letters):
        self.value = value
        self.counted_letters = counted_letters
        self.vowels = Counter()
        self.consonants = Counter()
        self.language = ''
        self.vowel_or_consonant()
        self.syllables = self.count_syllables()

    def vowel_or_consonant(self):
        eng_vowels = 'aeiouy'
        rus_vowels = 'аоуэыяеюиё'
        pattern = re.compile('[a-z]')
        if pattern.match(self.value):
            self.language = 'en'
            for char in self.value:
                if char in eng_vowels:
                    self.vowels.update(char)
                else:
                    self.consonants.update(char)
        else:
            self.language = 'ru'
            for char in self.value:
                if char in rus_vowels:
                    self.vowels.update(char)
                else:
                    self.consonants.update(char)

    def count_syllables(self):
        syllables = pyphen.Pyphen(lang=self.language).inserted(self.value)
        return dict(Counter(syllables.split("-")))


class FileParser:
    def __init__(self, text_from_file):
        self.text = text_from_file
        self.full_file_stat, self.counter_of_all_words = self.get_all_file_statistic()
        self.get_most_and_least_common_words()

    def get_all_file_statistic(self):
        file_stat_dict = {
            "average_word_length": 0,
            "vowels": Counter(),
            "consonants": Counter(),
            "syllables": Counter()
        }
        en_words = Counter()
        ru_words = Counter()
        for token in tokenize(self.text):
            file_stat_dict["average_word_length"] += token.counted_letters
            file_stat_dict["vowels"].update(token.vowels)
            file_stat_dict['consonants'].update(token.consonants)
            file_stat_dict['syllables'].update(token.syllables)
            if token.language == 'en':
                en_words.update([token.value])
            if token.language == 'ru':
                ru_words.update([token.value])

        total_number_of_words = sum(en_words.values()) + sum(ru_words.values())
        file_stat_dict["average_word_length"] = (file_stat_dict['average_word_length'] /
                                                 total_number_of_words) if total_number_of_words else 0

        return file_stat_dict, [ru_words, en_words]

    def get_most_and_least_common_words(self):
        ru_words, en_words = map(dict, self.counter_of_all_words)

        most_common = []
        least_common = []

        if len(ru_words) + len(en_words) != 0:
            min_freq = min(freq for word, freq in chain(ru_words.items(), en_words.items()))
            max_freq = max(freq for word, freq in chain(ru_words.items(), en_words.items()))

            least_common = [word for word, freq in chain(ru_words.items(), en_words.items())
                            if freq == min_freq][:3]
            most_common = [word for word, freq in chain(ru_words.items(), en_words.items())
                           if freq == max_freq][:3]

        self.full_file_stat.update({"most_recent_word": most_common, "least_recent_word": least_common})

    def return_full_file_statistics(self):
        return self.full_file_stat

    def return_all_words_counter(self):
        return self.counter_of_all_words


class WordStatistic:
    def __init__(self, word):
        self.word = word.lower()
        self.language = ''
        self.get_word_language()

    @staticmethod
    def validate_word(word: str):
        return word if re.match('[a-z -]|[а-яё -]', word.lower()) else None

    def get_word_language(self):
        if self.word.lower().startswith(string.ascii_lowercase):
            self.language = 'en'
        else:
            self.language = 'ru'

    def get_word_length(self):
        return len(self.word)

    def get_vowels_and_consonants(self):
        vowels = 'aeiouyаоуэыяеюиё'
        consonants = 'qwrtpsdfghjklzxcvbnmйцкнгшщзхъфвпрлджэчсмтбь'
        word_vowels = Counter()
        word_consonants = Counter()
        for char in self.word:
            if char in vowels:
                word_vowels.update(char)
            if char in consonants:
                word_consonants.update(char)
        return dict(word_vowels), dict(word_consonants)

    def get_syllables_stat(self):
        syllables = pyphen.Pyphen(lang=self.language).inserted(self.word)
        return dict(Counter(syllables.split("-")))

    def return_all_statistic_for_word(self):
        return {
            'word': self.word,
            'number_of_letters': self.get_word_length(),
            'vowels': self.get_vowels_and_consonants()[0],
            'consonants': self.get_vowels_and_consonants()[1],
            'syllables': self.get_syllables_stat()
        }
