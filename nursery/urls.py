from django.urls import path
from . import views

urlpatterns = [
    path('', views.PetListView.as_view(), name='pet_list'),
    path('<int:pk>/', views.PetDetailView.as_view(), name='pet_detail'),
    path('create/', views.PetCreateView.as_view(), name='pet_create'),
    path('<int:pk>/update/', views.PetUpdateView.as_view(), name='pet_update'),
    path('<int:pk>/delete/', views.PetDeleteView.as_view(), name='pet_delete'),
]