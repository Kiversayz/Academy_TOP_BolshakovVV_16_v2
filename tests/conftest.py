import pytest
import requests

@pytest.fixture(scope="session")
def BASE_URL():
    """ Получение базовой части ссылки """
    
    url = "http://127.0.0.1:8000"
    return url


@pytest.fixture(scope="session")
def get_token(BASE_URL):
    """ Получаем токен через API """
    
    auth_response = requests.post(f"{BASE_URL}/api/auth/token/", json={
        "username": "testuser",
        "password": "ys6-xRK-6y6-H8y"
    })
    
    token = auth_response.json()['access']
    return token

@pytest.fixture(scope="session")
def token_in_headers(get_token):
    """ Используем токен для доступа к API """
    
    return {"Authorization": f"Bearer {get_token}"}


@pytest.fixture(scope="session")
def neg_token_in_headers(get_token):
    """ Используем токен для доступа к API """
    
    return {"Authorization": f"Bearer {get_token}1"}

@pytest.fixture
def create_pet_nursery(BASE_URL, token_in_headers):
    """ Создаем питомца через API с валидным токеном """
    data_json = {
        "name": "Тест питомец",
        "animal_type": "dog",
        "breed": "Тесттерьер",
        "family": "Тестировых",
        "age": 12,
        "price": "500",
        "currency": "RUB",
        "hypoallergenic": 'false',
        "feeding_type": "Мясо, овощи, тесты",
        "description": "Создан чтобы проводить тесты"
    }
    response = requests.post(
        url=f"{BASE_URL}/nursery/pet/",
        headers=token_in_headers,
        json=data_json
    )
    
    assert response.status_code in [200, 201], f"Ошибка: {response.json()}"
    pet = response.json()
    
    yield pet
    
    delete_response = requests.delete(
        url=f"{BASE_URL}/nursery/pet/{pet['id']}/",
        headers=token_in_headers,
    )
    assert delete_response.status_code == 204 , f"Ошибка: {delete_response.json()}"

@pytest.fixture
def create_petcomments_core(BASE_URL, token_in_headers, create_pet_nursery):
    """ Создаем комментарий через API с валидным токеном """
    pet_id = create_pet_nursery['id']
    test_data = {
        "author_name": "Testus",
        "content": "test string",
        "pet": pet_id
    }
    response = requests.post(
        url=f"{BASE_URL}/api/petcomments/",
        headers=token_in_headers,
        json=test_data  # ← используй json
    )
    # Проверка статуса
    assert response.status_code in [200, 201], f"Ошибка: {response.json()}"
    
    data_response = response.json()
    
    yield data_response
    
    # Удаляем созданный комментарий
    delete_response = requests.delete(
        url=f"{BASE_URL}/api/petcomments/{data_response['id']}/",
        headers=token_in_headers
    )
    assert delete_response.status_code == 204, f"Ошибка при удалении: {delete_response.json()}"