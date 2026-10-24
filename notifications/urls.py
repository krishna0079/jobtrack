"""Notifications app — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list_view, name='notifications'),
    path('<str:notif_id>/read/', views.mark_read_view, name='notification_read'),
    path('mark-all-read/', views.mark_all_read_view, name='notifications_mark_all'),
]
