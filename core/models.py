from django.db import models
from nursery.models import Pet
from django.contrib.auth.models import User

# Create your models here.
#оставлю модель на будущее, в друг добавлю товары для питомника
class Product(models.Model):
    """ Простейшая модель для проверки соединения. """
    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product'  # Имя таблицы в базе данных
        verbose_name = 'Товар'  # Название модели в админке
        verbose_name_plural = "Товары" # Имя множественного числа модели в админке

    def __str__(self):
        return f'{self.name} - {self.price}'

class PetComment(models.Model):
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор") # ДОБАВЛЯЕМ
    content = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата комментария")

    class Meta:
        db_table = 'core_petcomment'
        verbose_name = 'Комментарий'
        verbose_name_plural = "Комментарии"
        # Добавляем ordering для сортировки по умолчанию (старые первыми)
        ordering = ['created_at'] 

    def __str__(self):
        return f"Комментарий к {self.pet.name} от {self.author.username}"


