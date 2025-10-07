from django.views.generic import CreateView, DetailView, UpdateView, TemplateView, ListView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from .models import UserProfile
from django.utils.decorators import method_decorator
import random
import string
from django.contrib.auth.models import User


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


class UserProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm # Убедитесь, что форма существует
    template_name = 'user/profile_update.html' # Убедитесь, что шаблон существует
    # success_url можно определить в get_success_url

    def get_object(self, queryset=None):
        """Получаем профиль пользователя, которого хотим редактировать."""
        user_pk = self.kwargs.get('pk') # Получаем pk из URL
        target_user = get_object_or_404(User, pk=user_pk)
        profile, created = UserProfile.objects.get_or_create(user=target_user)
        return profile

    def test_func(self):
        """Проверяем, может ли текущий пользователь редактировать этот профиль."""
        profile_to_edit = self.get_object() # Получаем профиль, который хотим редактировать
        current_user = self.request.user

        # Владелец может редактировать свой профиль
        if profile_to_edit.user == current_user:
            return True
        # Модератор может редактировать профиль, но не админа
        elif current_user.groups.filter(name='Moderator').exists() and not profile_to_edit.user.is_superuser:
            return True
        # Админ может редактировать любой профиль
        elif current_user.is_superuser:
            return True
        # В остальных случаях - запрет
        return False

    def get_success_url(self):
        """Куда перенаправить после успешного обновления."""
        # Перенаправляем на страницу профиля пользователя, которого редактировали
        return reverse_lazy('user:user_detail', kwargs={'pk': self.object.user.pk}) # type: ignore # Используем пространство имен

    # Убедитесь, что reverse_lazy импортирован и используется правильно
    from django.urls import reverse_lazy


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


class UserListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'user/user_list.html'
    context_object_name = 'users'

    def get_queryset(self):
        user = self.request.user

        # Если пользователь — админ или модератор
        if user.is_staff or user.is_superuser:
            # Показываем всех пользователей
            queryset = User.objects.all().order_by('username')
        else:
            # Показываем только обычных пользователей (не модераторов/админов)
            queryset = User.objects.filter(is_staff=False, is_superuser=False).order_by('username')

        # Перемещаем текущего пользователя в начало списка
        if user in queryset:
            queryset = [user] + [u for u in queryset if u != user]

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_user'] = self.request.user
        return context

class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'user/user_detail.html'
    context_object_name = 'target_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        target_user = self.get_object()
        user = self.request.user

        # Проверяем, можно ли редактировать
        context['can_edit_profile'] = (
            target_user == user or  # Пользователь смотрит сам себя
            (user.is_staff and not target_user.is_superuser) or  # Модератор смотрит неадмина # type: ignore
            user.is_superuser  # Админ
        )
        context['can_change_password'] = target_user == user  # Только сам может менять пароль

        # Получаем профиль
        profile, created = UserProfile.objects.get_or_create(user=target_user)
        context['profile'] = profile

        return context