from django.urls import path
from api.views.company_views import (
    RegisterCompanyView,
    GetCompanyView,
    GetCompanyByIdView,
    UpdateCompanyView
)

urlpatterns = [
    path('register/', RegisterCompanyView.as_view()),
    path('', GetCompanyView.as_view()),
    path('<str:company_id>/', GetCompanyByIdView.as_view()),
    path('update/<str:company_id>/', UpdateCompanyView.as_view()),
]
