"""Interviews app — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.interview_list_view, name='interviews'),
    path('add/<str:app_id>/', views.interview_add_view, name='interview_add'),
    path('<str:interview_id>/', views.interview_detail_view, name='interview_detail'),
    path('<str:interview_id>/edit/', views.interview_edit_view, name='interview_edit'),
    path('<str:interview_id>/delete/', views.interview_delete_view, name='interview_delete'),
]
