"""
URL configuration for AcademyTop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    html = """
    <!doctype html>
    <html lang="ru">
      <head>
        <meta charset="utf-8">
        <title>Привет!</title>
      </head>
      <body>
        <h1>Привет! Django + MSSQL работает.</h1>
      </body>
    </html>
    """
    # Указываем charset явно
    return HttpResponse(html, content_type="text/html")

urlpatterns = [
    path('', home, name='home'),             # ← корневой URL
    path('admin/', admin.site.urls),        # стандартный админ
    path('api/', include('core.urls')),         # API core попадает в корень сайта
    path('nursery/', include('nursery.urls')),      # API nursery попадает в корень сайта
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)