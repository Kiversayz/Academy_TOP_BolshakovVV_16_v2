from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import UserProfile

# Создаем класс UserProfileInline, который будет использоваться для отображения профиля пользователя в админке
class UserProfileInline(admin.StackedInline):
    model = UserProfile     # Указываем модель, которая будет отображаться в этом inline
    can_delete = False      # Запрещаем удаление связанной записи (UserProfile) через этот inline
    verbose_name_plural = 'Профиль'     # Устанавливаем название для отображения в админке
    fk_name = 'user'        # Указываем имя поля, которое связывает модель UserProfile с моделью User

# Создаем класс UserAdmin, который наследуется от BaseUserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]       # Добавляем inline-модель UserProfile к админке пользователя


admin.site.unregister(User)     # Отменяем регистрацию стандартного класса UserAdmin для модели User
admin.site.register(User, UserAdmin)        # Регистрируем модель User с новым классом UserAdmin