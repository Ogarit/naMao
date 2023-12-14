from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('registerServices/', views.register_services, name='new_services'),
    path('services/<str:service_id>/', views.services, name='services'),
    path('logout/', views.logout, name='logout')
]
