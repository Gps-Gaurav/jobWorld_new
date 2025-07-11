
from django.urls import path
from api.views.auth_views import RegisterView, LoginView

urlpatterns = [
    path("user/register", RegisterView.as_view()),
    path("user/login", LoginView.as_view()),
]
