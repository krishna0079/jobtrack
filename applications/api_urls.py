"""Applications API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.applications_api, name='api_applications'),
    path('<str:app_id>/', api_views.application_detail_api, name='api_application_detail'),
]
