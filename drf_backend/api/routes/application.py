from django.urls import path
from api.views.application_views import (
    ApplyJobView,
    GetAppliedJobsView,
    GetApplicantsView,
    UpdateApplicationStatusView
)

urlpatterns = [
    path('apply/<str:job_id>', ApplyJobView.as_view(), name='apply-job'),
    path('applied/', GetAppliedJobsView.as_view(), name='get-applied-jobs'),
    path('applicants/<str:job_id>', GetApplicantsView.as_view(), name='get-applicants'),
    path('update/<str:app_id>', UpdateApplicationStatusView.as_view(), name='update-status'),
]
