from django.db import models
from django.urls import reverse

# Create your models here.

class Pet(models.Model):
    ANIMAL_TYPES = [
        ('dog', 'Собака'),
        ('cat', 'Кошка'),
        ('bird', 'Птица'),
        ('fish', 'Рыба'),
        ('other', 'Другое'),
    ]
    name = models.CharField(max_length=100, verbose_name="Кличка")
    animal_type = models.CharField(max_length=20, choices=ANIMAL_TYPES, verbose_name="Тип животного")
    breed = models.CharField(max_length=100, verbose_name="Порода")
    family = models.CharField(max_length=100, verbose_name="Семейство")
    age = models.PositiveIntegerField(verbose_name="Возраст (в месяцах)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=3, default="RUB", verbose_name="Валюта")
    hypoallergenic = models.BooleanField(default=False, verbose_name="Гипоаллергенный")
    feeding_type = models.TextField(verbose_name="Рацион питания", blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    image = models.ImageField(upload_to='pets/', verbose_name="Фотография", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        db_table = 'nursery_pet'  # Имя таблицы в базе данных
        verbose_name = 'Питомник'  # Название модели в админке
        verbose_name_plural = "Питомники" # Имя множественного числа модели в админке

    def __str__(self):
        return f"{self.name} ({self.breed})"

    def get_absolute_url(self):
        return reverse("pet_detail", kwargs={"pk": self.pk})