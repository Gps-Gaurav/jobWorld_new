from django.urls import path
from api.views.company_views import CompanyListView

urlpatterns = [
    path('', CompanyListView.as_view()),
]
