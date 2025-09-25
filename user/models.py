from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')         # Связь с пользователем Django через OneToOneField
    phone = models.CharField(max_length=15, blank=True, null=True)      # Поле для хранения номера телефона пользователя
    birth_date = models.DateField(blank=True, null=True)        # Поле для хранения даты рождения пользователя
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)         # Поле для хранения аватара пользователя с указанием пути загрузки
    city = models.CharField(max_length=100, blank=True, null=True)          # Поле для города, максимальная длина 100 символов, может быть пустым
    bio = models.TextField(blank=True, null=True)       # Поле для биографии, может быть пустым
    is_premium = models.BooleanField(default=False)         # Поле для статуса премиум-пользователя, по умолчанию False

    def __str__(self):          # Метод для строкового представления объекта
        return f"{self.user.username}'s profile"        # Возвращаем строку с именем пользователя и словом "profile"
