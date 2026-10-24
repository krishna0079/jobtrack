"""REST API URL Configuration"""
from django.urls import path, include

urlpatterns = [
    path('jobs/', include('jobs.api_urls')),
    path('applications/', include('applications.api_urls')),
    path('interviews/', include('interviews.api_urls')),
    path('notifications/', include('notifications.api_urls')),
    path('profile/', include('accounts.api_urls')),
]
