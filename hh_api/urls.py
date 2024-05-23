from django.urls import path
from . import views

urlpatterns = [
    # path('authorize/', views.authorize, name='authorize'),
    # path('callback/', views.callback, name='callback'),
    # path('token/', views.token_view, name='token'),
    #    path('vacancies/', views.search_vacancies, name='vacancies'),
    path('vacancies/', views.search_vacancies, name='search_vacancies'),
]
