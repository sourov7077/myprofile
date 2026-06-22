# portfolio/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.project_list, name='projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('contact/', views.contact, name='contact'),
    path('jokes/', views.jokes, name='jokes'),
]
