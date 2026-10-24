"""Dashboard app — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
]
