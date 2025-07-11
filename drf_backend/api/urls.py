
from django.urls import path
from api.views.auth_views import RegisterView, LoginView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
]
