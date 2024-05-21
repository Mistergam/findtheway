from django.urls import path
from . import views


urlpatterns = [
    path('authorize/', views.authorize, name='authorize'),
    path('', views.index, name='index'),
]
