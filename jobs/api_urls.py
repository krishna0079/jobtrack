"""Jobs API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.jobs_api, name='api_jobs'),
    path('<str:job_id>/', api_views.job_detail_api, name='api_job_detail'),
]
