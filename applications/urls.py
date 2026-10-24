"""Applications app — URLs"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.application_list_view, name='applications'),
    path('mark-applied/<str:job_id>/', views.mark_applied_view, name='mark_applied'),
    path('<str:app_id>/', views.application_detail_view, name='application_detail'),
    path('<str:app_id>/update/', views.application_update_view, name='application_update'),
    path('<str:app_id>/delete/', views.application_delete_view, name='application_delete'),
]
