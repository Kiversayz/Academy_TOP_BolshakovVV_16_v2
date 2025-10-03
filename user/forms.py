from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Создаём профиль автоматически
            UserProfile.objects.create(user=user)
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'birth_date', 'avatar', 'city', 'bio']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class UserPasswordChangeForm(PasswordChangeForm):
    # PasswordChangeForm — уже включает:
    # - old_password
    # - new_password1
    # - new_password2 (подтверждение)
    # Мы можем добавить кастомные валидаторы или изменить виджеты
 
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Можем настроить виджеты (например, placeholder)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Старый пароль'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Новый пароль'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Подтверждение пароля'})