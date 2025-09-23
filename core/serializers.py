from rest_framework import serializers
from .models import Product

""" 
serializers.ModelSerializer – базовый класс, который автоматически генерирует поля на основе модели.
Meta.model указывает, к какой модели относится сериализатор.
fields = "__all__" – значит «включить все поля модели в JSON». Можно указать конкретный список, если нужно скрыть что‑то.
"""

class ProductSerializer(serializers.ModelSerializer):
    """Как переводить Product ↔ JSON."""
    class Meta:
        model = Product             # → источник данных
        fields = '__all__'          # → все поля модели (id, name, price, created)