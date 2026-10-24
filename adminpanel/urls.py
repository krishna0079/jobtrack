"""Admin Panel — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('users/', views.admin_users_view, name='admin_users'),
    path('companies/', views.admin_companies_view, name='admin_companies'),
    path('companies/add/', views.admin_company_add_view, name='admin_company_add'),
    path('companies/<str:comp_id>/edit/', views.admin_company_edit_view, name='admin_company_edit'),
    path('companies/<str:comp_id>/delete/', views.admin_company_delete_view, name='admin_company_delete'),
    path('jobs/', views.admin_jobs_view, name='admin_jobs'),
    path('jobs/auto-fetch/', views.admin_job_fetch_view, name='admin_job_fetch'),
    path('jobs/add/', views.admin_job_add_view, name='admin_job_add'),
    path('jobs/<str:job_id>/edit/', views.admin_job_edit_view, name='admin_job_edit'),
    path('jobs/<str:job_id>/delete/', views.admin_job_delete_view, name='admin_job_delete'),
]
