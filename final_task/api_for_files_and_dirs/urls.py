from django.urls import path, include
from rest_framework import routers
from api_for_files_and_dirs import views


router = routers.DefaultRouter()
router.register(r'file', views.FileViewSet)
router.register(r'directory', views.DirectoryViewSet)
router.register(r'word', views.WordVS, basename="WordStat")

urlpatterns = [
    path('', include(router.urls)),
    path('directory/<slug:pk>',
         views.DirectoryViewSet.as_view({'get': 'retrieve'}),
         name="number_of_files"),

    path('file/<slug:pk>',
         views.FileViewSet.as_view({'get': 'retrieve'}),
         name="number_of_files"),

    path('word/<str:word>',
         views.WordVS.get,
         name='word_statistic'),

    path('supported_extensions',
         views.show_acceptable_extensions),

    path('choose_extension',
         views.choose_extensions_to_analyze)
]
