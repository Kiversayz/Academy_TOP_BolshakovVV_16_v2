import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    """
    Создает и возвращает экземпляр APIClient для тестирования API.

    Returns:
        APIClient: Экземпляр клиента для выполнения HTTP-запросов в тестах.
    """
    return APIClient()

@pytest.fixture
def authenticated_user():
    """
    Создает аутентифицированного пользователя и генерирует JWT токен для него.

    Returns:
        tuple: Кортеж из пользователя (User) и access токена (str).
    """
    user = User.objects.create_user(username="testuser", password="12345")
    refresh = RefreshToken.for_user(user)
    return user, str(refresh.access_token)