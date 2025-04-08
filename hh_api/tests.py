import os
import django

# Указываем настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "findtheway.settings")
django.setup()

from hh_api.services.hh_api import load_vacancies, fetch_vacancy_text
from hh_api.analyzers.skills_analyzer import categorize_requirements


def test_vacancies_list():
    search_text = "Python"
    vacancies = load_vacancies(search_text, per_page=50, max_pages=2)
    print(vacancies[0])
    raw_data = fetch_vacancy_text(vacancies[0])
    reqs = raw_data["Требования"]
    duties = raw_data["Обязанности"]
    fetched_vacancies_count = raw_data["Обработанные вакансии"]

    categorized_requirements = categorize_requirements(reqs)

    vacancies_list = {
        item["name"]: item["alternate_url"]
        for item in vacancies[0]
    }

    print("vacancies_list:")
    for name, url in vacancies_list.items():
        print(f"{name} -> {url}")

if __name__ == "__main__":
    test_vacancies_list()
