"""Accounts API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.profile_api, name='api_profile'),
]
