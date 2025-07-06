# backend/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/user/', include('api.routes.user')),
    # path('api/v1/company/', include('api.routes.company')),
    # path('api/v1/job/', include('api.routes.job')),
    # path('api/v1/application/', include('api.routes.application')),
    # path('api/v1/dashboard/', include('api.routes.dashboard')),
    # path('', TemplateView.as_view(template_name='index.html')),  # fallback
]
