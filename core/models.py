from django.db import models

# Create your models here.
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
