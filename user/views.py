from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from .models import UserProfile
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
import random
import string


def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Генерируем случайный пароль
            password = generate_password(length=8)  # Можно настроить длину
            user = form.save(commit=False)  # Не сохраняем в БД пока
            user.set_password(password)      # Устанавливаем сгенерированный пароль
            user.save()                      # Теперь сохраняем

            # Отправляем письмо с паролем
            subject = 'Добро пожаловать в AcademyTop!'
            message = f'Привет, {user.username}!\n\nТвой сгенерированный пароль: {password}\n\nПожалуйста, измените его после входа в систему.\n\nС уважением,\nОт AcademyTop - Студент Большаков Валерий'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            
            # Авто вход поле авторизации
            """ login(request, user)
            return redirect('profile') """
            
            # Показываем сообщение о том что регистрация успешно и необходимо проверить почту чтобы узнать пароль.
            return render(request, 
                          'user/registration_success.html', 
                          {'email': user.email, 'username': user.username}
                          )
    else:
        form = UserRegistrationForm()

    return render(request, 'user/register.html', {'form': form})

@method_decorator(login_required, name='dispatch')
class UserPasswordChangeView(PasswordChangeView):
    form_class = UserPasswordChangeForm
    template_name = 'user/password_change.html'
    success_url = reverse_lazy('profile')  # Куда перейти после смены пароля

    def form_valid(self, form):
        # Можем добавить дополнительную логику (например, отправить уведомление)
        return super().form_valid(form)

    def form_invalid(self, form):
        # Можем добавить логику при ошибке (например, логировать)
        return super().form_invalid(form)

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    return render(request, 'user/profile.html', {'profile': profile})

@login_required
def profile_update(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'user/profile_update.html', {'form': form})

def generate_password(length=12, use_digits=True, use_uppercase=True, use_lowercase=True, use_symbols=True):
    """
    Генерирует случайный пароль по заданному паттерну.
    
    :param length: Длина пароля (по умолчанию 12)
    :param use_digits: Использовать ли цифры (0-9)
    :param use_uppercase: Использовать ли заглавные буквы (A-Z)
    :param use_lowercase: Использовать ли строчные буквы (a-z)
    :param use_symbols: Использовать ли спецсимволы (!@#$%^&*)
    :return: Сгенерированный пароль
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