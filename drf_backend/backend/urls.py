# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from core.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),

    # Include all API routes from api/urls.py
    path('api/', include('api.urls')),
]