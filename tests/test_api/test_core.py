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