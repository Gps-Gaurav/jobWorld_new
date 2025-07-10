from django.urls import path
from api.views.dashboard_view import DashboardView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard-endpoint'),
]
