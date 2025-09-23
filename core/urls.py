from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'products', ProductViewSet)        # → /api/products/ …

urlpatterns = [
    path('api/', include(router.urls))              # «вклеиваем» все сгенерированные пути
]
