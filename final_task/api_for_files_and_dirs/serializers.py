from rest_framework import serializers
from background_parser.models import FileStatistic, DirectoryStatistic


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FileStatistic
        fields = ['file', 'slug', 'most_recent_word', 'least_recent_word',
                  'average_word_length', 'vowels', 'consonants']


class DirectorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DirectoryStatistic
        fields = ['directory_name', 'slug', 'files_and_dirs', 'number_of_files',
                  'most_recent_word', 'least_recent_word',
                  'average_word_length', 'vowels', 'consonants']


class WordSerializer(serializers.Serializer):
    word = serializers.CharField(max_length=50)
    number_of_letters = serializers.IntegerField()
    vowels = serializers.JSONField()
    consonants = serializers.JSONField()
    syllables = serializers.JSONField()
