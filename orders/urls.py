from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    path('', views.home, name='home'),
    path('login/customer/', views.customer_login, name='customer_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('register/', views.register, name='register'),
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('edit_customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),  # Düzenleme için URL
    path('delete_customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),  # Silme URL'si
    path('admin_dashboard/add-customer/', views.add_customer, name='add_customer'),
    path('generate_random_customers/', views.generate_random_customers, name='generate_random_customers'),
    path('delete_all_customers/', views.delete_all_customers, name='delete_all_customers'),
    # Tüm kullanıcıları silme URL'si

    # Diğer URL desenleri...

]
