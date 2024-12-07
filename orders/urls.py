from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/customer/', views.customer_login, name='customer_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('register/', views.register, name='register'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
]
