from django.db import models

# Create your models here.


class DirectoryStatistic(models.Model):
    slug = models.SlugField(primary_key=True, default="default", max_length=100)
    directory_name = models.CharField(max_length=100)
    files_and_dirs = models.JSONField()
    number_of_files = models.IntegerField()
    most_recent_word = models.CharField(max_length=100)
    least_recent_word = models.CharField(max_length=100)
    average_word_length = models.FloatField()
    vowels = models.JSONField()
    consonants = models.JSONField()
    syllables = models.JSONField(default={})


class FileStatistic(models.Model):
    slug = models.SlugField(primary_key=True, default="default", max_length=100)
    file = models.CharField(max_length=100)
    most_recent_word = models.CharField(max_length=1000)
    least_recent_word = models.CharField(max_length=1000)
    average_word_length = models.FloatField()
    vowels = models.JSONField()
    consonants = models.JSONField()
    syllables = models.JSONField(default={})
