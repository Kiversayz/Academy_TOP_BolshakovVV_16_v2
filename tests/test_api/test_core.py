import pytest
import requests


def test_token_use_it(token_in_headers, BASE_URL):
    """ Используем валидный токен для доступа к API """
    response = requests.get(f"{BASE_URL}/api/petcomments/", headers= token_in_headers)
    
    assert response.status_code == 200 , f"Ошибка: {response.json()}"

def test_neg_token_use_it(neg_token_in_headers, BASE_URL):
    """ Используем НЕ валидный токен для доступа к API """
    response = requests.get(f"{BASE_URL}/api/petcomments/", headers= neg_token_in_headers)
    
    assert response.status_code == 401 , f"Ошибка: {response.json()}"

def test_post_api_petcomments(BASE_URL, token_in_headers, create_petcomments_core, create_pet_nursery):
    """ Создаем комментарий через API с валидным токеном """
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