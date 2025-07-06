from django.urls import path
from api.views.user_views import UserListView

urlpatterns = [
    path('', UserListView.as_view()),
]