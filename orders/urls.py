from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Ana sayfa
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # Çıkış yapma için
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
path('customer-login/', views.customer_login, name='customer_login'),
    path('admin-login/', views.admin_login, name='admin_login'),

]
