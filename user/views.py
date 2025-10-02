from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UserRegistrationForm, UserProfileForm, UserPasswordChangeForm
from .models import UserProfile
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('profile')  # Перенаправляем на профиль
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