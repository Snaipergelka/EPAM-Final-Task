from background_parser.models import FileStatistic
from background_parser.opener import get_content
from background_parser.parser import FileParser


class StatisticCalculator:
    """
    Abstract class for classes that calculating statistic.
    """
    def calculate_stat(self):
        pass


class FileAnalyzer(StatisticCalculator):
    """
    Opens file by get_content, invokes parser
    and saves statistics of the file into database.
    """
    def __init__(self, filename):
        self.filename = filename
        self.parser: FileParser = None

    def calculate_stat(self):
        """
        Invokes FileParser to calculate statistic.
        """
        self.parser = FileParser(get_content(filename=self.filename))
        return (self.parser.return_full_file_statistics(),
                self.parser.return_all_words_counter())

    def save_stat(self):
        """
        Saves statistic into database.
        """
        stat = self.parser.return_full_file_statistics()
        FileStatistic.objects.update_or_create(
            slug=self.filename[2:].replace(".", "-").replace("/", "-"),
            defaults={"file": self.filename,
                      "most_recent_word": stat["most_recent_word"],
                      "least_recent_word": stat["least_recent_word"],
                      "average_word_length": stat['average_word_length'],
                      "vowels": stat['vowels'],
                      "consonants": stat['consonants'],
                      "syllables": stat['syllables']})
