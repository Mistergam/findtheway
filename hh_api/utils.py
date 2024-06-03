from .models import JobVacancy, ProfessionalRole


def filter_vacancies_by_keywords(query):
    filtered_vacancies = []
    query_keywords = query.lower().split()

    roles = ProfessionalRole.objects.all()
    for role in roles:
        role_keywords = role.get_keywords()
        if any(keyword in role_keywords for keyword in query_keywords):
            vacancies = JobVacancy.objects.filter(professional_role=role)
            filtered_vacancies.extend(vacancies)

        return filtered_vacancies