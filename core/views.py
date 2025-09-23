from django.shortcuts import render
from rest_framework import viewsets, permissions
from .models import Product
from .serializers import ProductSerializer

# Create your views here.

""" 
- viewsets.ModelViewSet – готовый класс, который уже реализует все действия. 
Не нужно писать отдельные функции‑контроллеры.
- queryset – откуда брать данные (по умолчанию берёт всё).
- serializer_class – какой сериализатор использовать для ввода/вывода.
- permission_classes – список проверок прав; IsAuthenticated требует, 
чтобы запрос прошёл через JWT-аутентификатор, который мы подключили в settings.py (REST_FRAMEWORK).
"""

class ProductViewSet(viewsets.ModelViewSet):
    """
    Полный набор CRUD-операций для Product:
    - GET /api/products/           → список
    - POST /api/products/          → создать
    - GET /api/products/<id>/      → детали
    - PUT /api/products/<id>/      → полное обновление
    - PATCH /api/products/<id>/    → частичное обновление
    - DELETE /api/products/<id>/   → удалить
    """
    
    queryset = Product.objects.all()            # набор всех записей
    serializer_class = ProductSerializer        # какой сериализатор использовать
    permission_classes = [permissions.IsAuthenticated]  # только авторизованны с JWT‑токеном

