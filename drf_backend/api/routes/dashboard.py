from django.urls import path
from api.views import dashboard_view

urlpatterns = [
    path('user-stats/', dashboard_view.get_user_stats),
    path('application-trends/', dashboard_view.get_application_trends),
    path('user-skills/', dashboard_view.get_user_skills),
    path('global-stats/', dashboard_view.get_global_stats),
]