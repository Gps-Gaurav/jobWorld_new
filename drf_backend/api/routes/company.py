from django.urls import path
from api.views.company_view import CompanyView

urlpatterns = [
    path('', CompanyView.as_view(), name='company-endpoint'),
]
