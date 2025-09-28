import requests
import time

BASE_URL = 'http://127.0.0.1:8000'

def test_get_pets_list():
    """ Тестируем получение списка питомцев и питомника"""
    response = requests.get(f'{BASE_URL}/nursery/')
    assert response.status_code == 200
    assert "Питомцы в продаже" in response.text  # заголовок из шаблона


