from django.test import TestCase
from .models import JobVacancy, ProfessionalRole
from .utils import filter_vacancies_by_keywords


class JobVacancyTestCase(TestCase):

    def setUp(self):
        # Создаем профессиональные роли и вакансии для тестирования
        developer_role = ProfessionalRole.objects.create(name="Developer", keywords="python, django, programming")
        designer_role = ProfessionalRole.objects.create(name="Designer", keywords="photoshop, design, creative")

        JobVacancy.objects.create(title="Python Developer", description="Develop web applications using Django.", professional_role=developer_role)
        JobVacancy.objects.create(title="Web Designer", description="Design user interfaces and experiences.", professional_role=designer_role)

    def test_filter_vacancies_by_keywords(self):
        # Тестируем фильтрацию вакансий по ключевым словам

        # Тестируем ключевое слово "python"
        query = "python"
        filtered_vacancies = filter_vacancies_by_keywords(query)
        self.assertEqual(len(filtered_vacancies), 1)
        self.assertEqual(filtered_vacancies[0].title, "Python Developer")

        # Тестируем ключевое слово "design"
        query = "design"
        filtered_vacancies = filter_vacancies_by_keywords(query)
        self.assertEqual(len(filtered_vacancies), 1)
        self.assertEqual(filtered_vacancies[0].title, "Web Designer")

        # Тестируем ключевое слово "creative"
        query = "creative"
        filtered_vacancies = filter_vacancies_by_keywords(query)
        self.assertEqual(len(filtered_vacancies), 1)
        self.assertEqual(filtered_vacancies[0].title, "Web Designer")

        # Тестируем ключевое слово "django"
        query = "django"
        filtered_vacancies = filter_vacancies_by_keywords(query)
        self.assertEqual(len(filtered_vacancies), 1)
        self.assertEqual(filtered_vacancies[0].title, "Python Developer")

        # Тестируем ключевое слово, которое не соответствует ни одной вакансии
        query = "java"
        filtered_vacancies = filter_vacancies_by_keywords(query)
        self.assertEqual(len(filtered_vacancies), 0)
