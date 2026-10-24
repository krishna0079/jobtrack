"""Notifications API URLs"""
from django.urls import path
from . import api_views

urlpatterns = [
    path('', api_views.notifications_api, name='api_notifications'),
    path('<str:notif_id>/read/', api_views.notification_read_api, name='api_notification_read'),
]
