from django.urls import include, path
from rest_framework import routers

from api_for_files_and_dirs import views

router = routers.DefaultRouter()
router.register(r'file', views.FileViewSet)
router.register(r'directory', views.DirectoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('directory/<slug:pk>',
         views.DirectoryViewSet.as_view({'get': 'retrieve'}),
         name="number_of_files"),

    path('file/<slug:pk>',
         views.FileViewSet.as_view({'get': 'retrieve'}),
         name="number_of_files"),

    path('word/<str:word>',
         views.get_word_statistic,
         name='word_statistic'),

    path('supported_extensions',
         views.show_acceptable_extensions,
         name='supported_extension'),

    path('start',
         views.choose_extensions_to_analyze,
         name='start_analyze')
]
