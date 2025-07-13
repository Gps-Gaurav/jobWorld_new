

from django.urls import path, include

urlpatterns = [

    # Versioned API v1
    path('v1/', include([
        path('user/', include('api.routes.user')),
        path('company/', include('api.routes.company')),
        path('job/', include('api.routes.job')),
        path('application/', include('api.routes.application')),
        path('dashboard/', include('api.routes.dashboard')),
    ])),
]
