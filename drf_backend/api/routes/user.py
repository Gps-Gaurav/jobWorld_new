from django.urls import path
from api.views.user_views import UserView

urlpatterns = [
    path('', UserView.as_view(), name='user-endpoint'),
]
