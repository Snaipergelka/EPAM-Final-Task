from collections import Counter
from typing import Dict, List

from background_parser.file_analyzer import FileAnalyzer
from background_parser.models import DirectoryStatistic


class ContentStatistic:
    def __init__(self):
        self.__content_stat = Counter({
            "vowels": Counter(),
            "consonants": Counter(),
            "en_word_freq": Counter(),
            "ru_word_freq": Counter(),
            "syllables": Counter(),
        })
        self.__average_content_stat = {
            "amount_of_words": 0,
            "average_word_length": 0.0,
        }

    def merge_statistic(self, stat: Dict):
        content_keys = self.__content_stat.keys()

        self.__content_stat.update(
            {
                k: v for k, v in stat.items()
                if k in content_keys
            })

        amount_of_words = (sum(stat["en_word_freq"].values()) +
                           sum(stat["ru_word_freq"].values()))
        total = (self.__average_content_stat['amount_of_words'] +
                 amount_of_words)

        if total == 0:
            return

        prev_average = self.__average_content_stat['average_word_length']
        self.__average_content_stat['average_word_length'] = \
            (self.__average_content_stat['amount_of_words'] * prev_average +
             amount_of_words * stat['average_word_length']) / total

        self.__average_content_stat['amount_of_words'] = total

    def get_statistic(self):
        return {**self.__content_stat, **self.__average_content_stat}


class FilesStatisticAggregator:
    def __init__(self, files: List[FileAnalyzer]):
        self.files = files
        self.__content_statistic = ContentStatistic()

    def calculate_and_aggregate_statistic(self):
        for file in self.files:
            general_stat, word_frequency = file.calculate_stat()
            file.save_stat()
            general_stat['ru_word_freq'] = word_frequency[0]
            general_stat['en_word_freq'] = word_frequency[1]

            self.__content_statistic.merge_statistic(general_stat)

        return self.__content_statistic.get_statistic()


class FolderStatisticAggregator:
    def __init__(self):
        self.__folder_statistic = {
            "number_of_files": 0,
            "files": [],
            "dirs": [],
        }

        self.__content_statistic = ContentStatistic()

    def add_files_statistic(self, stat: Dict):
        """
        Adds statistic from files which are in the folder itself.
        (not in the sub-folders)
        """
        self.__content_statistic.merge_statistic(stat)

    def add_children_folder_stat(
            self,
            sub_folders_stats: 'FolderStatisticAggregator'):
        """
        Adds statistics from sub-folders
        """
        self.__merge_folder_statistic(sub_folders_stats.get_stat())
        self.__content_statistic.merge_statistic(
            sub_folders_stats.get_content_content_statistics())

    def add_files_and_folders_info(self, files: List[str], dirs: List[str]):

        self.__folder_statistic["files"] += files
        self.__folder_statistic["number_of_files"] += len(files)
        self.__folder_statistic["dirs"] += dirs

    def __merge_folder_statistic(self, stat: Dict):
        for k in self.__folder_statistic:
            self.__folder_statistic[k] = self.__folder_statistic[k] + stat[k]

    def get_stat(self):
        return {
            **self.__content_statistic.get_statistic(),
            **self.__folder_statistic
        }

    def get_content_content_statistics(self):
        return self.__content_statistic.get_statistic()

    def save_stat(self, dir_name):

        most_freq_word = ""
        least_freq_word = ""
        stat = self.__content_statistic.get_statistic()

        if stat['en_word_freq'] or stat['ru_word_freq']:
            most_freq_word = max(
                stat['en_word_freq'].most_common(1) +
                stat['ru_word_freq'].most_common(1),
                key=lambda x: x[1]
            )[0]

            least_freq_word = min(
                stat['en_word_freq'].most_common()[-1:] +
                stat['ru_word_freq'].most_common()[-1:],
                key=lambda x: x[1]
            )[0]

        DirectoryStatistic.objects.update_or_create(
            slug=dir_name[2:].replace(".", "-").replace("/", "-"),
            defaults={
                "directory_name": dir_name,
                "files_and_dirs": {
                    "files": self.__folder_statistic['files'],
                    "dirs": self.__folder_statistic['dirs']
                },
                "number_of_files": self.__folder_statistic['number_of_files'],
                "most_recent_word": most_freq_word,
                "least_recent_word": least_freq_word,
                "average_word_length": stat['average_word_length'],
                "vowels": stat['vowels'],
                "consonants": stat['consonants'],
                "syllables": stat['syllables']
            })
