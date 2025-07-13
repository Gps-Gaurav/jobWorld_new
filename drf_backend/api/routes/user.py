# api/routes/user.py
from django.urls import path

from api.views.user_views import RegisterView, LoginView, LogoutView, RefreshTokenView, ChangePasswordView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]
