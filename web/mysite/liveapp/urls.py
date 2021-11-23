from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.index_template, name='index_template'),
]
