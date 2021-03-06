import json

from api_for_files_and_dirs.serializers import (DirectorySerializer,
                                                FileSerializer)
from background_parser.models import DirectoryStatistic, FileStatistic
from background_parser.parser import WordStatistic
from background_parser.services import analyze_folder_and_save_results
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets


class FileViewSet(viewsets.ModelViewSet):
    queryset = FileStatistic.objects.all()
    serializer_class = FileSerializer


class DirectoryViewSet(viewsets.ModelViewSet):
    queryset = DirectoryStatistic.objects.all()
    serializer_class = DirectorySerializer


def get_word_statistic(request, word):

    if WordStatistic.validate_word(word) is None:
        return JsonResponse({
            word: "Word is not valid"
        })
    else:
        word_init = WordStatistic(word)
        stat = word_init.return_all_statistic_for_word()
        return JsonResponse(stat)


def show_acceptable_extensions(request):
    return JsonResponse({"extensions": [".txt", ".py", ".csv",
                                        ".doc", ".docx", ".eml",
                                        ".epub", ".json", ".html",
                                        ".odt", ".pdf", ".xlsx",
                                        ".xls", ".rtf"]})


@csrf_exempt
def choose_extensions_to_analyze(request):
    if request.method == "POST":

        analyze_folder_and_save_results(
            json.loads(request.body)["directory"],
            json.loads(request.body)["extensions"],
            repeat=10)

        return JsonResponse({
            "result": "started calculation"
        })
    return JsonResponse({
            "error": "Method is not allowed!"
        })
