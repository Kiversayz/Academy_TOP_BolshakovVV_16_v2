from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

# Создаем представление для модели Product с помощью ModelViewSet
# ModelViewSet автоматически реализует все CRUD-операции (создание, чтение, обновление, удаление)
class ProductViewSet(viewsets.ModelViewSet):
    """
    Полный набор CRUD-операций для модели Product:
    - GET /api/products/           → получение списка всех продуктов
    - POST /api/products/          → создание нового продукта
    - GET /api/products/<id>/      → получение деталей конкретного продукта
    - PUT /api/products/<id>/      → полное обновление продукта
    - PATCH /api/products/<id>/    → частичное обновление продукта
    - DELETE /api/products/<id>/   → удаление продукта

    Все эти операции доступны через API-эндпоинты, которые автоматически создаются Django REST Framework.
    """
    # Определяем, из какой модели брать данные для представления
    queryset = Product.objects.all()
    
    # Указываем, какой сериализатор использовать для преобразования данных
    # Сериализатор отвечает за преобразование объектов модели в JSON и обратно
    serializer_class = ProductSerializer

    # Определяем права доступа к ресурсу
    # IsAuthenticated означает, что только авторизованные пользователи (с JWT-токеном)
    # могут выполнять операции с продуктами
    permission_classes = [permissions.IsAuthenticated]

