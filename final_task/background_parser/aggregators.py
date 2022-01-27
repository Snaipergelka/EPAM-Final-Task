from collections import Counter
from typing import List

from background_parser.file_analyzer import FileAnalyzer
from background_parser.models import DirectoryStatistic


class FilesStatisticAggregator:
    """
    Calculates and aggregates all files' statistic.
    """
    def __init__(self, files: List[FileAnalyzer]):
        self.files = files
        self.aggregated_statistic = {
            "number_of_files": len(files),
            "amount_of_words": 0,
            "average_word_length": 0.0,
            "vowels": Counter(),
            "consonants": Counter(),
            "en_word_freq": Counter(),
            "ru_word_freq": Counter(),
            "syllables": Counter()
        }

        self.average_lengths = []

    def calculate_and_aggregate_statistic(self) -> dict:
        """
        Goes through every file statistic and merges it.
        """
        for file in self.files:
            general_stat, word_frequency = file.calculate_stat()
            file.save_stat()

            self.merge_general_stats(general_stat)
            self.merge_word_frequency_stats(*word_frequency)

            # save info about avg length of word in a file and total number of words
            # it is used to calculate average length across all files
            self.average_lengths.append(
                (
                    general_stat['average_word_length'],
                    sum(word_frequency[0].values()) + sum(word_frequency[1].values())
                )
            )

        # combine statistic for word average length
        total_number_of_words = sum(i[1] for i in self.average_lengths)

        self.aggregated_statistic['average_word_length'] = sum(
            avg_length * (number_of_words / total_number_of_words)
            for avg_length, number_of_words in self.average_lengths) if total_number_of_words else 0
        self.aggregated_statistic['amount_of_words'] = total_number_of_words

        return self.aggregated_statistic

    def merge_general_stats(self, general_stat: dict):
        """
        Merges vowels, consonants and syllables statistic from files.
        :param dict general_stat: general statistic of file.
        """
        self.aggregated_statistic["vowels"].update(general_stat["vowels"])
        self.aggregated_statistic["consonants"].update(general_stat["consonants"])
        self.aggregated_statistic["syllables"].update(general_stat["syllables"])

    def merge_word_frequency_stats(self, word_frequency_ru: Counter, word_frequency_en: Counter):
        """
        Merges word frequency statistic from files.
        :param Counter word_frequency_ru: file russian word frequency.
        :param Counter word_frequency_en: file english word frequency.
        """
        self.aggregated_statistic["ru_word_freq"].update(word_frequency_ru)
        self.aggregated_statistic["en_word_freq"].update(word_frequency_en)


class FolderStatisticAggregator:
    """
    Merges all files statistics into folder statistic and pushes it into database.
    """
    def __init__(self):
        # TODO probably it is better to separate these statistics
        self.__stats = {
            "number_of_files": 0,
            "files": [],
            "dirs": [],
            "amount_of_words": 0,
            "average_word_length": 0.0,
            "vowels": Counter(),
            "consonants": Counter(),
            "en_word_freq": Counter(),
            "ru_word_freq": Counter(),
            "syllables": Counter()
        }

    def add_files_statistic(self, files_stats: dict):
        """
        Adds files statistic to the folder statistic.
        :param dict files_stats: file statistic.
        """
        self.__merge_stat(files_stats)

    def add_children_folder_stat(self, sub_folders_stats):
        """
        Adds children folders statistic to the parent folder statistic.
        :param sub_folders_stats: sub folders' statistic.
        """
        self.__merge_stat(sub_folders_stats.get_stat())

    def add_files_and_folders_info(self, files, dirs):
        """
        Adds files and folders paths into a folder statistic.
        """
        self.__stats["files"] = self.__stats["files"] + files
        self.__stats["dirs"] = self.__stats["dirs"] + dirs

    def __merge_stat(self, stat):
        """
        Merges all the statistic (files and children-folders).
        """
        overall_amount_of_words = self.__stats['amount_of_words'] + stat['amount_of_words']
        if overall_amount_of_words == 0:
            return
        self.__stats['number_of_files'] = self.__stats['number_of_files'] + stat['number_of_files']

        self.__stats['average_word_length'] = (self.__stats['amount_of_words'] * self.__stats['average_word_length'] +
                                               stat['amount_of_words'] * stat["average_word_length"]) / \
                                               overall_amount_of_words

        self.__stats['amount_of_words'] = overall_amount_of_words

        self.__stats["vowels"].update(stat["vowels"])
        self.__stats["consonants"].update(stat["consonants"])
        self.__stats["en_word_freq"].update(stat["en_word_freq"])
        self.__stats["ru_word_freq"].update(stat["ru_word_freq"])
        self.__stats["syllables"].update(stat["syllables"])

    def get_stat(self):
        """
        Returns folder statistic.
        """
        return self.__stats

    def save_stat(self, dir_name):
        """
        Saves folder statistic to database.
        """
        most_freq_word = ""
        least_freq_word = ""

        if self.__stats['en_word_freq'] or self.__stats['ru_word_freq']:
            most_freq_word = max(
                self.__stats['en_word_freq'].most_common(1) +
                self.__stats['ru_word_freq'].most_common(1),
                key=lambda x: x[1]
            )[0]

            least_freq_word = min(
                self.__stats['en_word_freq'].most_common()[-1:] +
                self.__stats['ru_word_freq'].most_common()[-1:],
                key=lambda x: x[1]
            )[0]

        DirectoryStatistic.objects.update_or_create(
            slug=dir_name[2:].replace(".", "-").replace("/", "-"),
            defaults={
                "directory_name": dir_name,
                "files_and_dirs": {
                    "files": self.__stats['files'],
                    "dirs": self.__stats['dirs']
                },
                "number_of_files": self.__stats['number_of_files'],
                "most_recent_word": most_freq_word,
                "least_recent_word": least_freq_word,
                "average_word_length": self.__stats['average_word_length'],
                "vowels": self.__stats['vowels'],
                "consonants": self.__stats['consonants'],
                "syllables": self.__stats['syllables']
            })
