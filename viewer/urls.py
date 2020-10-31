from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('/<uuid:directory_id>/', views.browse, name='browse'),
    path('/<uuid:directory_id>/<str:file>/', views.file, name='file')
]
