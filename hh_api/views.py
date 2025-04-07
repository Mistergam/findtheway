from django.http import JsonResponse
from django.shortcuts import render
import json

from .services.hh_api import load_vacancies, fetch_vacancy_text
from .analyzers.skills_analyzer import categorize_requirements, remove_duplicates

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
    try:
        vacancies = load_vacancies(search_text, per_page=50, max_pages=2)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    raw_data = fetch_vacancy_text(vacancies[0])
    reqs = raw_data["Требования"]
    duties = raw_data["Обязанности"]
    fetched_vacancies_count = raw_data["Обработанные вакансии"]

    categorized_requirements = categorize_requirements(reqs)

    context = {
        'professional_roles': vacancies[3],
        'vacancies_found': vacancies[1],
        'filtered_vacancies': vacancies[2],
        'knowledges': categorized_requirements["Знания"],
        'skills': categorized_requirements["Умения"],
        'cans': categorized_requirements["Владение"],
        'duties': duties,
        'fetched': fetched_vacancies_count
    }

    return render(request, 'vacancies.html', context)
