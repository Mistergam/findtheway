from bs4 import BeautifulSoup


def extract_section_text(tag):
    """Извлекает текст из списка <ul> или набора <p>."""
    values = []
    next_tag = tag.find_next()

    while next_tag and next_tag.name not in ('strong', 'p', 'br'):
        if next_tag.name == 'ul':
            values.extend([li.text.strip() for li in next_tag.find_all('li')])
            break
        elif next_tag.name == 'p':
            values.append(next_tag.text.strip())
        next_tag = next_tag.find_next()

    return values


def parse_vacancy_description(text, result, counted_vacancies):
    """Парсит HTML-описание вакансии и добавляет данные в итоговый словарь."""
    soup = BeautifulSoup(text, 'html.parser')

    # Ключевые слова для определения секций
    duties_keywords = ["обязанност", "задачи", "чем вы будете заниматься"]
    requirements_keywords = ["требовани", "что мы ждем", "предпочтения"]

    vacancy_matched = False

    for tag in soup.find_all(['strong', 'p']):
        key_text = tag.text.strip().lower()

        if any(keyword in key_text for keyword in duties_keywords):
            result["Обязанности"].extend(extract_section_text(tag))
            vacancy_matched = True
        elif any(keyword in key_text for keyword in requirements_keywords):
            result["Требования"].extend(extract_section_text(tag))
            vacancy_matched = True

    if vacancy_matched:
        counted_vacancies["processed_count"] += 1



