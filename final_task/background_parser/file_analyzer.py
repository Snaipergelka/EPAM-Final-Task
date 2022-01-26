from background_parser.models import FileStatistic
from background_parser.opener import get_content
from background_parser.parser import FileParser


class StatisticCalculator:
    def calculate_stat(self):
        pass


class FileAnalyzer(StatisticCalculator):
    def __init__(self, filename):
        self.filename = filename
        self.parser: FileParser = None

    def calculate_stat(self):
        self.parser = FileParser(get_content(filename=self.filename))
        return self.parser.return_full_file_statistics(), self.parser.return_all_words_counter()

    def save_stat(self):
        FileStatistic.objects.update_or_create(
            slug=self.filename[2:].replace(".", "-").replace("/", "-"),
            defaults={   "file": self.filename,
                         "most_recent_word": self.parser.return_full_file_statistics()["most_recent_word"],
                         "least_recent_word": self.parser.return_full_file_statistics()["least_recent_word"],
                         "average_word_length": self.parser.return_full_file_statistics()['average_word_length'],
                         "vowels": self.parser.return_full_file_statistics()['vowels'],
                         "consonants": self.parser.return_full_file_statistics()['consonants'],
                         "syllables": self.parser.return_full_file_statistics()['syllables']
                     })
