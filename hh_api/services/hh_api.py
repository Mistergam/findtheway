from collections import Counter, defaultdict
import requests

from hh_api.services.parse_vacancies import parse_vacancy_description


# this function extracts and filters vacancies data and returns four things: list of vacancies data dicts,
# initial count, filtered count, dict of allowed professional roles used for filtering.
def load_vacancies(search_text, per_page=100, max_pages=15):
    search_url = 'https://api.hh.ru/vacancies'
    params = {
        'text': search_text,
        'per_page': per_page,
        'area': 1,
        'page': 0,
    }

    vacancies = []
    for page in range(max_pages):
        params['page'] = page
        response = requests.get(search_url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data['items']
            vacancies.extend(items)
            if len(items) < per_page:
                break
        else:
            raise Exception(response.json().get('description', 'Failed to retrieve data'))

    vacancies_found = len(vacancies)
    role_counter = defaultdict(int)
    for vacancy in vacancies:
        for role in vacancy.get('professional_roles', []):
            role_counter[role['name']] += 1

    threshold = vacancies_found * 0.05
    allowed_roles = {role: count for role, count in role_counter.items() if count > threshold}
    vacancies = [vacancy for vacancy in vacancies if vacancy['professional_roles'][0]['name'] in allowed_roles]
    vacancies_filtered = len(vacancies)

    return vacancies, vacancies_found, vacancies_filtered, allowed_roles


def fetch_vacancy_text(vacancies):
    """Обрабатывает список вакансий и возвращает итоговый словарь с обязанностями и требованиями и количеством обработанных вакансий."""
    result = {"Обязанности": [], "Требования": []}
    counted_vacancies = {'processed_count': 0}

    for vacancy in vacancies:
        response = requests.get(vacancy["url"])
        data = response.json()
        text = data.get('branded_description') or data.get('description', '')
        parse_vacancy_description(text, result, counted_vacancies)
    result['Обработанные вакансии'] = counted_vacancies["processed_count"]

    return result
