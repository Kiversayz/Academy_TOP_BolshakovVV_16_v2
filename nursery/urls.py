from django.urls import path
from . import views
from django.views.decorators.cache import cache_page

app_name = 'nursery'

urlpatterns = [
    path('', views.PetListView.as_view(), name='pet_list'),
    # --- Конкретные пути ---
    path('create/', views.PetCreateView.as_view(), name='pet_create'),
    # --- Пути с переменными ---
    # ВАЖНО: <slug:slug> должен идти ПОСЛЕ конкретных путей, таких как 'create/'
    path('<slug:slug>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('<slug:slug>/update/', views.PetUpdateView.as_view(), name='pet_update'),
    path('<slug:slug>/delete/', views.PetDeleteView.as_view(), name='pet_delete'),
    path('<slug:slug>/deactivate/', views.PetDeactivateView.as_view(), name='pet_deactivate'),
    path('<slug:slug>/activate/', views.PetActivateView.as_view(), name='pet_activate'),
    # --- Пути для комментариев ---
    path('<int:pet_id>/comments/', views.PetCommentsListView.as_view(), name='pet_comments_list'),
]