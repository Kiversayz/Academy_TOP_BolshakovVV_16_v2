from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    # 1. Конкретные пути (например, 'profile/')
    path('profile/', views.UserProfileView.as_view(), name='profile'),  # ← Для текущего пользователя
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('password/change/', views.UserPasswordChangeView.as_view(), name='password_change'),

    # 2. Пути с переменными (например, <int:pk>/)
    path('list/', views.UserListView.as_view(), name='user_list'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),  # ← Для просмотра любого пользователя
    # ВНИМАНИЕ: этот путь должен быть после /profile/update/, иначе может быть конфликт
    path('<int:pk>/profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),

    # 3. Другие
    path('register/', views.UserRegistrationView.as_view(), name='register_user'),
    path('registration/success/', views.RegistrationSuccessView.as_view(), name='registration_success'),
]