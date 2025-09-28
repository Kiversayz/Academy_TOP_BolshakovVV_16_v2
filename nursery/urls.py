from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

#Создаём экземпляр DefaultRouter
router = DefaultRouter()
router.register(r'pet', views.PetViewSet)  # → /api/petcomments/ …
urlpatterns = [
    path('', include(router.urls))              # «вклеиваем» все сгенерированные пути
]

urlpatterns = [
    path('', views.pet_list, name='pet_list'),
    path('', include(router.urls)),
    path('<int:pk>/', views.pet_detail, name='pet_detail'),
]
