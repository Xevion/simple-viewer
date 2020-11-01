from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('add/submit', views.submit_new, name='add_submit'),
    path('<uuid:directory_id>/', views.browse, name='browse'),
    path('<uuid:directory_id>/refresh', views.refresh, name='refresh'),
    path('<uuid:directory_id>/<str:file>/', views.file, name='file'),
    path('<uuid:directory_id>/<str:file>/generate', views.generate_thumb, name='generate_thumb'),

]
