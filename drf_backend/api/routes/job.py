from django.urls import path
from api.views.job_view import JobView

urlpatterns = [
    path('', JobView.as_view(), name='job-endpoint'),
]
