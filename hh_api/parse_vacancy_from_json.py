import json
import time
from collections import Counter

from bs4 import BeautifulSoup
import requests
from django.http import JsonResponse


def extract_section_text(tag):
    """Извлекает текст из списка <ul> или набора <p>."""
    entries = []
    next_tag = tag.find_next()

    while next_tag and next_tag.name not in ('strong', 'p', 'br'):
        if next_tag.name == 'ul':
            entries.extend([li.text.strip() for li in next_tag.find_all('li')])
            break
        elif next_tag.name == 'p':
            entries.append(next_tag.text.strip())
        next_tag = next_tag.find_next()

    return values


def parse_vacancy_description(text):
    """Парсит HTML-описание вакансии и выделяет Обязанности и Требования."""
    soup = BeautifulSoup(text, 'html.parser')

    result = {"Обязанности": [], "Требования": []}

    # Ключевые слова для определения секций
    duties_keywords = ["обязанност", "задачи", "чем вы будете заниматься"]
    requirements_keywords = ["требовани", "что мы ждем", "предпочтения"]

    for tag in soup.find_all(['strong', 'p']):
        key_text = tag.text.strip().lower()

        if any(keyword in key_text for keyword in duties_keywords):
            result["Обязанности"].extend(extract_section_text(tag))
        elif any(keyword in key_text for keyword in requirements_keywords):
            result["Требования"].extend(extract_section_text(tag))

    return result


search_url = 'https://api.hh.ru/vacancies'
per_page = 10
max_pages = 10 // per_page
delay_between_requests = 0.1

# Задаем параметры поиска
params = {
    'text': "python",
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
    # time.sleep(delay_between_requests)

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

result = {}


for vacancy in vacancies:
    vac_url = vacancy["url"]
    # print(vac_url)
    # print(vacancy['salary'])
    response = requests.get(vac_url)
    time.sleep(0.1)
    data = response.json()
    if data['branded_description']:
        text = data['branded_description']
    else:
        text = data['description']
    soup = BeautifulSoup(text, 'html.parser')

    for strong_tag in soup.find_all('strong'):
        key = strong_tag.text.strip()
        if 'обязанност' in key.lower():
            key = "Обязанности"
        elif 'требовани' in key.lower():
            key = "Требования"

        ul_tag = strong_tag.find_next('ul')
        if ul_tag:
            values = [li.text.strip() for li in ul_tag.find_all('li')]
        else:
            values = []
            next_tag = strong_tag.find_next()
            while next_tag and next_tag.name not in ('strong', 'br'):
                if next_tag.name == 'p':
                    values.append(next_tag.text.strip())
                next_tag = next_tag.find_next()
        if values:
            if key in result:
                result[key].extend(values)
            else:
                result[key] = values

    if len(result) == 0:
        for p_tag in soup.find_all('p'):
            key = p_tag.text.strip()
            ul_tag = p_tag.find_next('ul')
            if ul_tag:
                values = [li.text.strip() for li in ul_tag.find_all('li')]
            if values:
                if key in result:
                    result[key].extend(values)
                else:
                    result[key] = values

with open('results.json', 'w', encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)


    # for key, values in result.items():
    #     if not key:
    #         print('OTHER STUFF:')
    #     elif key[-1] == ':':
    #         print(key)
    #     else:
    #         print(f'{key}:')
    #     for value in values:
    #         print(f'  - {value}')
