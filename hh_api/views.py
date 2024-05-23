# import json
from collections import Counter

import nltk
from django.shortcuts import render, redirect
# import urllib.parse
import requests
from django.http import JsonResponse
import time

from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')


def index(request):
    return render(request, 'index.html')


# def authorize(request):
#     client_id = 'your_client_id'
#     redirect_uri = urllib.parse.quote('http://127.0.0.1:8000/callback/')
#     auth_url = f'https://hh.ru/oauth/authorize?response_type=code&client_id={client_id}&state=xyz&redirect_uri={redirect_uri}'
#     return redirect(auth_url)
#
#
# def callback(request):
#     code = request.GET.get('code')
#     client_id = 'your_client_id'
#     client_secret = 'your_client_secret'
#     redirect_uri = 'http://127.0.0.1:8000/callback/'
#
#     token_url = 'https://hh.ru/oauth/token'
#     data = {
#         'grant_type': 'authorization_code',
#         'client_id': client_id,
#         'client_secret': client_secret,
#         'code': code,
#         'redirect_uri': redirect_uri
#     }
#     response = requests.post(token_url, data=data)
#     return JsonResponse(response.json())
#
#
# def get_access_token():
#     client_id = 'your_client_id'
#     client_secret = 'your_client_secret'
#     token_url = 'https://hh.ru/oauth/token'
#
#     data = {
#         'grant_type': 'client_credentials',
#         'client_id': client_id,
#         'client_secret': client_secret
#     }
#
#     response = requests.post(token_url, data=data)
#     return response.json()
#
#
# def token_view(request):
#     token_data = get_access_token()
#     return JsonResponse(token_data)
#
#
# def search_vacancies_with_auth(request):
#     token_data = get_access_token()
#     access_token = token_data['access_token']
#
#     headers = {
#         'Authorization': f'Bearer {access_token}',
#         'User-Agent': 'your-app-name'
#     }
#
#     search_url = 'https://api.hh.ru/vacancies'
#     params = {
#         'text': 'Python developer',
#         'area': '1'  # Example: 1 for Moscow
#     }
#
#     response = requests.get(search_url, headers=headers, params=params)
#     return JsonResponse(response.json())


def search_vacancies(request):
    search_text = request.GET.get('text', '')

    search_url = 'https://api.hh.ru/vacancies'
    per_page = 50
    max_pages = 100 // per_page
    delay_between_requests = 0.1

    params = {
        'text': search_text,
        'per_page': per_page,
        'area': 1,
        'page': 0
    }

    vacancies = []

    for page in range(max_pages):
        params['page'] = page
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # with open('json_file' + str(page) + '.json', 'w', encoding='utf8') as file:
            #     json.dump(data, file, ensure_ascii=False, indent=3)
            vacancies.extend(data['items'])
            if len(data['items']) < per_page:
                break
        else:
            error_message = response.json().get('description', 'Failed to retrieve data')
            return JsonResponse({'error': 'Failed to retrieve data'}, status=response.status_code)
        time.sleep(delay_between_requests)

    # Collecting data for analysis
    requirements = []
    responsibilities = []
    professional_roles = set()

    for vacancy in vacancies:
        if 'snippet' in vacancy:
            requirements.append(vacancy['snippet'].get('requirement', '') or '')
            responsibilities.append(vacancy['snippet'].get('responsibility', '') or '')
            professional_roles.add(vacancy['professional_roles'][0].get('name', '') or '')

    requirements_clean = [x.replace('highlighttext', '') for x in requirements]
    responsibilities_clean = [x.replace('highlighttext', '') for x in responsibilities]
    common_requirements = analyze_text(requirements_clean)
    common_responsibilities = analyze_text(responsibilities_clean)

    context = {
        'vacancies': vacancies,
        'common_requirements': common_requirements,
        'common_responsibilities': common_responsibilities
    }

    return render(request, 'vacancies.html', context)


def analyze_text(text_list):
    stop_words = set(stopwords.words('russian'))
    all_words = []
    bigrams = []
    trigrams = []

    for text in text_list:
        words = word_tokenize(text)
        words = [word.lower() for word in words if word.isalpha()]
        words = [word for word in words if word not in stop_words]
        all_words.extend(words)
        bigrams.extend(ngrams(words, 2))
        trigrams.extend(ngrams(words, 3))

    word_freq = Counter(all_words).most_common(10)
    bigram_freq = Counter(bigrams).most_common(10)
    trigram_freq = Counter(trigrams).most_common(10)

    return {
        'words': word_freq,
        'bigrams': bigram_freq,
        'trigrams': trigram_freq
    }
