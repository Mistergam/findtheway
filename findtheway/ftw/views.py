from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

def index(request):
    return render(request, 'index.html')


def authorize(request):
    state = ''
    authorization_url = (
        'https://hh.ru/oauth/authorize?'
        f'response_type=code&'
        f'client_id={settings.HH_CLIENT_ID}&'
        f'state={state}&'
        f'redirect_uri={settings.HH_REDIRECT_URI}'
    )