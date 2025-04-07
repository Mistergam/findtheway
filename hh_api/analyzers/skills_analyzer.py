def get_words(text):
    """Разбивает строку на слова и возвращает множество уникальных слов"""
    return set(text.lower().split())


def calculate_similarity(str1, str2):
    """Вычисляет процент совпадений слов между двумя строками"""
    words1 = get_words(str1)
    words2 = get_words(str2)

    # Находим пересечение слов
    common_words = words1.intersection(words2)

    # Вычисляем процент совпадений
    similarity = len(common_words) / min(len(words1), len(words2)) * 100
    return similarity


def remove_duplicates(requirements, threshold=60):
    """Удаляет дубликаты строк по условию совпадения 80% слов"""
    result = []

    for req in requirements:
        # Проверяем каждую строку на наличие дубликатов
        is_duplicate = False
        for existing_req in result:
            similarity = calculate_similarity(req, existing_req)
            if similarity >= threshold:
                # Если строка уже есть, то добавляем более длинную
                if len(req.split()) > len(existing_req.split()):
                    result.remove(existing_req)
                    result.append(req)
                is_duplicate = True
                break

        if not is_duplicate:
            result.append(req)

    return result


def categorize_requirements(requirements):
    req_kwds = {
        "Знания": ["знание ", ],
        "Умения": ["умение ", ],
        "Владение": ["владение ", ],
        "Опыт": ["опыт ", ],
        "Образование": ["образование", ]
    }

    req_result = {
        "Знания": [],
        "Умения": [],
        "Владение": [],
        "Опыт": [],
        "Образование": []
    }
    for req in requirements:
        text = req.lower()
        for category, kwds in req_kwds.items():
            if any(kwd in text for kwd in kwds):
                req_result[category].append(req)

    for category, values in req_result.items():
        req_result[category] = remove_duplicates(values)

    return req_result
