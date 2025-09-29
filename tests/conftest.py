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