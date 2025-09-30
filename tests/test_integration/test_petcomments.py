import pytest
import requests

#Тесты по проверки правельной работоспособности CRUD операций с комментариями к петомцам

def test_post_api_petcomments(BASE_URL, token_in_headers, create_petcomments_core, create_pet_nursery):
    """ Проверяем конкретный свежесозданный комментарий и наличие связи с Петомцем"""
    comment_id = create_petcomments_core['id']
    pet_id = create_pet_nursery['id']

    response = requests.get(
        url=f"{BASE_URL}/api/petcomments/{comment_id}/",
        headers=token_in_headers,
    )
    data_response = response.json()

    # Проверка статуса и содержимого
    assert response.status_code in [200, 201], f"Ошибка: {response.json()}"
    assert data_response["author_name"] == "Testus" , f"Ошибка: {response.json()}"
    assert data_response["content"] == "test string" , f"Ошибка: {response.json()}"
    assert data_response['id'] ==  comment_id , f"Ошибка: {response.json()} - ожидался id: {comment_id}"
    assert data_response['pet'] ==  pet_id , f"Ошибка: {response.json()} - ожидался id: {pet_id}"


@pytest.mark.parametrize("data, expected_status, description", [
    # 1. Полное изменение (PUT)
    (
        {"author_name": "Testus_new", "content": "test string new", "pet": 2},
        200,
        "Полное изменение комментария"
    ),
    # 2. Изменение без изменений (PUT с теми же данными)
    (
        {"author_name": "Original Name", "content": "Original content", "pet": 1},
        200,
        "Изменение без изменений"
    ),
    # 3. Невалидное изменение — несуществующий ID
    (
        {"author_name": "New Name", "content": "New content", "pet": 1},
        404,
        "Попытка изменить несуществующий комментарий"
    ),
    # 4. Частичное изменение (PUT с не всеми полями)
    (
        {"content": "Updated content only"},
        400,
        "Частичное изменение через PUT (если API позволяет)"
    ),
])
def test_put_api_petcomments(
    BASE_URL, token_in_headers, create_pet_nursery, create_petcomments_core,
    data, expected_status, description
):
    # Определяем ID для запроса
    # Для кейса 3 используем несуществующий ID
    if "несуществующий" in description:
        comment_id = 99999  # заведомо несуществующий ID
        pet_id = create_pet_nursery['id']
        # Обновляем данные, чтобы они не конфликтовали
        data = {**data, "pet": pet_id}
    else:
        comment_id = create_petcomments_core['id']
        # Если в data есть pet, заменяем на существующий
        if "pet" in data:
            data = {**data, "pet": create_pet_nursery['id']}

    # Формируем URL
    url = f"{BASE_URL}/api/petcomments/{comment_id}/"

    # Выполняем PUT-запрос
    response = requests.put(url, headers=token_in_headers, json=data)

    # Проверяем статус
    assert response.status_code == expected_status, \
        f"Ожидали статус {expected_status}, получили {response.status_code}. Описание: {description}"

    # Если ожидаем 200, проверим содержимое
    if expected_status == 200:
        data_response = response.json()
        for key, value in data.items():
            assert data_response[key] == value, \
                f"Поле {key} ожидало {value}, получили {data_response.get(key)}. Описание: {description}"
        assert data_response['id'] == comment_id, \
            f"ID не совпадает: ожидал {comment_id}, получил {data_response.get('id')}. Описание: {description}"

# Тест изменения каждого конкретного редактируемого поля path


# Получение и проверка полного списка комментариев