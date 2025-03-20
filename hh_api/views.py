# import json
from collections import Counter, defaultdict

import nltk
# import urllib.parse
import requests
from django.http import JsonResponse
from django.shortcuts import render
from nltk import word_tokenize, ngrams
from nltk.corpus import stopwords

from .utils import filter_vacancies_by_keywords

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


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
    per_page = 100
    max_pages = 1500 // per_page
    delay_between_requests = 0.1

    # Задаем параметры поиска
    params = {
        'text': search_text,
        'per_page': per_page,
        'area': 1,
        'page': 0,
    }

    vacancies = []

    # собираем данные в переменную vacancies
    for page in range(max_pages):
        params['page'] = page
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            # this is used to load example of json from hh.api if needed to view actual structure
            # with open('json_file' + str(page) + '.json', 'w', encoding='utf8') as file:
            #     json.dump(data, file, ensure_ascii=False, indent=3)
            vacancies.extend(data['items'])
            if len(data['items']) < per_page:
                break
        else:
            error_message = response.json().get('description', 'Failed to retrieve data')
            return JsonResponse({'error': 'Failed to retrieve data'}, status=response.status_code)
        # time.sleep(delay_between_requests)
    vacancies_found = len(vacancies)

    # Сортируем данные по имени вакансии для выдачи на страницу в лексикографическом порядке
    vacancies.sort(key=lambda dic: dic['name'])

    # Выбираем роли из данных для использования в качестве фильтра (пока в качестве фильтра используется доля роли
    # в общем списке - если доля больше 2%, то роль используется)
    roles = [role['name'] for vacancy in vacancies for role in vacancy['professional_roles']]
    # roles_counter = Counter(roles)
    professional_roles = {
        role: count
        for role, count in sorted(Counter(roles).items(), key=lambda x: x[1], reverse=True)
        if count > len(vacancies) // 50}

    # Фильтруем данные о вакансиях по найденным отфильтрованным ролям.
    vacancies = list(filter(lambda x: x['professional_roles'][0]['name'] in professional_roles, vacancies))
    filtered_vacancies = len(vacancies)

    # Из общих данных отдельно для обработки формируем списки для анализа
    requirements = []
    responsibilities = []
    output_vacancies = defaultdict(int)

    for vacancy in vacancies:

        if 'snippet' in vacancy:
            requirements.append(vacancy['snippet'].get('requirement', '') or '')
            responsibilities.append(vacancy['snippet'].get('responsibility', '') or '')
        output_vacancies[vacancy['name']] += 1

    requirements_clean = [x.replace('highlighttext', '') for x in requirements]
    responsibilities_clean = [x.replace('highlighttext', '') for x in responsibilities]
    output_vacancies = dict(sorted(output_vacancies.items(), key=lambda item: item[1], reverse=True))

    # Анализируем текст
    common_requirements = analyze_text(requirements_clean)
    common_responsibilities = analyze_text(responsibilities_clean)

    context = {
        'vacancies': vacancies,
        'professional_roles': professional_roles,
        'common_requirements': common_requirements,
        'common_responsibilities': common_responsibilities,
        'vacancies_found': vacancies_found,
        'filtered_vacancies': filtered_vacancies,
        'output_vacancies': output_vacancies,
    }

    return render(request, 'vacancies.html', context)


def analyze_text(text_list):
    stop_words = set(stopwords.words('russian'))
    all_words = []
    bigrams = []
    trigrams = []

    for text in text_list:
        words = word_tokenize(text)  # альтернативное решение через регулярку words = re.findall(r"\b[\w'-]+\b", text)
        words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
        all_words.extend(words)
        bigrams.extend(ngrams(words, 2))  # альтернатива (более быстрая) без NLTK bigrams = list(zip(words, words[1:]))
        trigrams.extend(ngrams(words, 3))

    word_freq = Counter(all_words).most_common(10)
    bigram_freq = Counter(bigrams).most_common(10)
    trigram_freq = Counter(trigrams).most_common(10)

    return {
        'words': word_freq,
        'bigrams': bigram_freq,
        'trigrams': trigram_freq
    }


def search_filtered_vacancies(request):
    query = request.GET.get('query', '')
    if query:
        vacancies = filter_vacancies_by_keywords(query)
    else:
        vacancies = []
    return render(request, 'search_results.html', {'vacancies': vacancies, 'query': query})
