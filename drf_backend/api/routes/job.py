from django.urls import path
from api.views import job_view

urlpatterns = [
    path('allJobs', job_view.get_all_jobs),
    path('admin', job_view.get_jobs_by_admin),
    path('post', job_view.post_job),
    path('getJobById/<str:job_id>', job_view.get_job_by_id),
    path('getJobByAdmin', job_view.get_jobs_by_admin),
    path('<str:job_id>/update', job_view.update_job),
    path('<str:job_id>/delete', job_view.delete_job),
]
