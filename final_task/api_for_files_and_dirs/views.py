import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets

from api_for_files_and_dirs.serializers import FileSerializer, DirectorySerializer, WordSerializer
from background_parser.fs_analyzer import analyze_folder_and_save_results
from background_parser.models import FileStatistic, DirectoryStatistic
from background_parser.parser import WordStatistic


class FileViewSet(viewsets.ModelViewSet):
    queryset = FileStatistic.objects.all()
    serializer_class = FileSerializer


class DirectoryViewSet(viewsets.ModelViewSet):
    queryset = DirectoryStatistic.objects.all()
    serializer_class = DirectorySerializer


class WordVS(viewsets.ViewSet):

    def get(self,  word):

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

        analyze_folder_and_save_results(".", json.loads(request.body)["extensions"], repeat=10)

        return JsonResponse({
            "result": "started calculation"
        })
    return JsonResponse({
            "error": "Method is not allowed!"
        })
