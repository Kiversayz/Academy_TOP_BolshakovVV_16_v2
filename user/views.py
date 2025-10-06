from django.views.generic import CreateView, DetailView, UpdateView, TemplateView
from django.shortcuts import render
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required  # ← Добавь этот импорт
from .forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from .models import UserProfile
from django.utils.decorators import method_decorator
import random
import string


class UserRegistrationView(CreateView):
    """
    Регистрация нового пользователя.
    """
    form_class = UserRegistrationForm
    template_name = 'user/register.html'
    success_url = reverse_lazy('registration_success')  # Перенаправляем на страницу успеха

    def form_valid(self, form):
        # Генерируем случайный пароль
        password = self.generate_password(length=8)  # Можно настроить длину
        user = form.save(commit=False)  # Не сохраняем в БД пока
        user.set_password(password)      # Устанавливаем сгенерированный пароль
        user.save()                      # Теперь сохраняем

        # Отправляем письмо с паролем
        subject = 'Добро пожаловать в AcademyTop!'
        message = f'Привет, {user.username}!\n\nТвой сгенерированный пароль: {password}\n\nПожалуйста, измените его после входа в систему.\n\nС уважением,\nОт AcademyTop - Студент Большаков Валерий'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        # Не входим автоматически — пользователь должен проверить почту
        # login(self.request, user)

        # Возвращаем страницу с сообщением об успешной регистрации
        # (Мы не можем использовать success_url, потому что нам нужны username и email)
        return render(self.request, 'user/registration_success.html', {
            'email': user.email,
            'username': user.username
        })

    def generate_password(self, length=12, use_digits=True, use_uppercase=True, use_lowercase=True, use_symbols=True):
        """
        Генерирует случайный пароль по заданному паттерну.
        """
        characters = ''
        if use_digits:
            characters += string.digits  # '0123456789'
        if use_uppercase:
            characters += string.ascii_uppercase  # 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if use_lowercase:
            characters += string.ascii_lowercase  # 'abcdefghijklmnopqrstuvwxyz'
        if use_symbols:
            characters += '!@#$%^&*'

        if not characters:
            raise ValueError("Должен быть выбран хотя бы один тип символов")

        # Генерируем пароль
        password = ''.join(random.choice(characters) for i in range(length))
        return password


class RegistrationSuccessView(TemplateView):
    """
    Страница, показывающая, что регистрация прошла успешно.
    """
    template_name = 'user/registration_success.html'


class UserProfileView(LoginRequiredMixin, DetailView):
    """
    Просмотр профиля пользователя.
    """
    model = UserProfile
    template_name = 'user/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    Редактирование профиля пользователя.
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'user/profile_update.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


@method_decorator(login_required, name='dispatch')
class UserPasswordChangeView(PasswordChangeView):
    """
    Изменение пароля пользователя.
    """
    form_class = UserPasswordChangeForm
    template_name = 'user/password_change.html'
    success_url = reverse_lazy('profile')  # Куда перейти после смены пароля

    def form_valid(self, form):
        # Можем добавить дополнительную логику (например, отправить уведомление)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Можем добавить логику при ошибке (например, логировать)
        return super().form_invalid(form)