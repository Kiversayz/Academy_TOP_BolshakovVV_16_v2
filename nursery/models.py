from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from django.core.mail import send_mail
from AcademyTop import settings
import uuid
from django.utils.text import slugify

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
    deactivated_at = models.DateTimeField(verbose_name="Дата деактивации", blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    slug = models.SlugField(unique=True, blank=True, null=True, verbose_name="URL")
    
    class Meta:
        db_table = 'nursery_pet'  # Имя таблицы в базе данных
        verbose_name = 'Питомник'  # Название модели в админке
        verbose_name_plural = "Питомники" # Имя множественного числа модели в админке

    def __str__(self):
        return f"{self.name} ({self.breed})"

    def get_absolute_url(self):
        """Возвращает канонический URL для этого питомца."""
        return reverse('nursery:pet_detail', kwargs={'slug': self.slug})
    
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
    
    def is_active(self):
        """Возвращает True, если питомец активен (deactivated_at пуст)."""
        return self.deactivated_at is None

    def deactivate(self):
        """Деактивировать питомца (установить дату деактивации)."""
        if self.deactivated_at is None:
            self.deactivated_at = timezone.now()
            self.save()

    def activate(self):
        """Активировать питомца (очистить дату деактивации)."""
        if self.deactivated_at is not None:
            self.deactivated_at = None
            self.save()
    
    def can_deactivate(self, user):
        """Проверяет, может ли пользователь деактивировать питомца."""
        return (
            self.owner == user or  # Владелец
            user.groups.filter(name='Moderator').exists() or  # Модератор
            user.is_staff or  # Админ
            user.is_superuser
        )

    def can_delete(self, user):
        """Проверяет, может ли пользователь удалить питомца."""
        return user.is_staff or user.is_superuser
    
    def increment_view_count(self, user):
        """Увеличивает счётчик просмотров, если пользователь — не владелец."""
        if self.owner != user:
            self.views_count += 1
            self.save()
            # Если достигли 5 просмотров — отправить письмо
            if self.views_count == 5:
                self.send_popularity_notification()

    def send_popularity_notification(self):
        """Отправляет письмо владельцу, если питомец стал популярным."""
        subject = f'Ваш питомец {self.name} пользуется популярностью!'
        message = f'Привет!\n\nВаш питомец "{self.name}" уже достиг 5 просмотров.\n\nС уважением,\nКоманда AcademyTop'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [self.owner.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Генерируем базовый slug
            base_slug = slugify(self.name)
            # Если имя пустое или не содержит допустимых символов
            if not base_slug:
                base_slug = f"pet-{uuid.uuid4().hex[:8]}" # Уникальный slug
            slug = base_slug
            counter = 1
            # Проверяем на уникальность и добавляем суффикс при необходимости
            while Pet.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Pedigree(models.Model):
    pet = models.OneToOneField('Pet', on_delete=models.CASCADE, related_name='pedigree')  # ← Одна родословная на одного питомца
    mother = models.CharField(max_length=100, verbose_name="Мать", blank=True, null=True)
    father = models.CharField(max_length=100, verbose_name="Отец", blank=True, null=True)
    generation = models.PositiveIntegerField(verbose_name="Поколение", default=1)
    breeding_date = models.DateField(verbose_name="Дата разведения", blank=True, null=True)
    notes = models.TextField(verbose_name="Примечания", blank=True, null=True)

    def __str__(self):
        return f"Родословная {self.pet.name}"