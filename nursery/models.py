from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date

# Create your models here.

class Pet(models.Model):
    ANIMAL_TYPES = [
        ('dog', 'Собака'),
        ('cat', 'Кошка'),
        ('bird', 'Птица'),
        ('fish', 'Рыба'),
        ('other', 'Другое'),
    ]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100, verbose_name="Кличка")
    animal_type = models.CharField(max_length=20, choices=ANIMAL_TYPES, verbose_name="Тип животного")
    breed = models.CharField(max_length=100, verbose_name="Порода")
    family = models.CharField(max_length=100, verbose_name="Семейство")
    birth_date = models.DateField(verbose_name="Дата рождения", blank=True, null=True)
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
    
    def clean(self):
        if self.birth_date:
            if self.birth_date > date.today():
                raise ValidationError("Дата рождения не может быть в будущем.")
            if self.birth_date < date.today().replace(year=date.today().year - 50):
                raise ValidationError("Дата рождения не может быть более 50 лет назад.")

    def get_age_in_months(self):
        """Возвращает возраст питомца в месяцах на основе даты рождения."""
        if not self.birth_date:
            return None  # Если дата рождения не указана — возраст неизвестен

        today = date.today()
        birth = self.birth_date

        # Разница в годах и месяцах
        year_diff = today.year - birth.year
        month_diff = today.month - birth.month

        # Общий возраст в месяцах
        age_in_months = year_diff * 12 + month_diff

        # Если день рождения в этом месяце ещё не наступил — вычитаем 1 месяц
        if today.day < birth.day:
            age_in_months -= 1

        return max(age_in_months, 0)  # Возраст не может быть отрицательным