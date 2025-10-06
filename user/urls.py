from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register_user'),
    path('registration/success/', views.RegistrationSuccessView.as_view(), name='registration_success'),  # ← Новый URL
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),
]