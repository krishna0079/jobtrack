"""Interviews API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.interviews_api, name='api_interviews'),
    path('<str:interview_id>/', api_views.interview_detail_api, name='api_interview_detail'),
]
