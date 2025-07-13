from django.urls import path
from api.views import dashboard_view

urlpatterns = [
    path('stats', dashboard_view.get_user_stats),
    path('trends', dashboard_view.get_application_trends),
    path('skills', dashboard_view.get_user_skills),
    path('global-stats', dashboard_view.get_global_stats),
]