from django.urls import path
from api.views.application_view import ApplicationView

urlpatterns = [
    path('', ApplicationView.as_view(), name='application-endpoint'),
]
