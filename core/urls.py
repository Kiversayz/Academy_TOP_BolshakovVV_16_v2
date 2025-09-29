from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, PetCommentViewSet, CustomTokenObtainPairView

""" 
DefaultRouter автоматически генерирует набор стандартных маршрутов для CRUD-операций 
(list, create, retrieve, update, destroy, …) по имени модели. 
"""

#Создаём экземпляр DefaultRouter
router = DefaultRouter()
#Регистрируем ViewSet для ProductViewSet
router.register(r'products', ProductViewSet)        # → /api/products/ …
#Регистрируем ViewSet для PetCommentViewSet
router.register(r'petcomments', PetCommentViewSet)  # → /api/petcomments/ …

urlpatterns = [
    path('', include(router.urls)),              # «вклеиваем» все сгенерированные пути
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
]
