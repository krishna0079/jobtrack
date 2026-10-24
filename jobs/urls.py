"""Jobs app — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list_view, name='jobs'),
    path('search/', views.job_search_view, name='job_search'),
    path('<str:job_id>/', views.job_detail_view, name='job_detail'),
    path('<str:job_id>/save/', views.save_job_view, name='save_job'),
    path('<str:job_id>/unsave/', views.unsave_job_view, name='unsave_job'),
]
