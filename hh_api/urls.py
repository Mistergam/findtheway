from django.urls import path
from . import views
from .views import search_filtered_vacancies


urlpatterns = [
    # path('authorize/', views.authorize, name='authorize'),
    # path('callback/', views.callback, name='callback'),
    # path('token/', views.token_view, name='token'),
    #    path('vacancies/', views.search_vacancies, name='vacancies'),
    path('vacancies/', views.search_vacancies, name='search_vacancies'),
    path('search/', search_filtered_vacancies, name='search_filtered_vacancies')
]
