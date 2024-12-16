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
    path('edit_customer/<int:customer_id>/', views.edit_customer, name='edit_customer'),  # Düzenleme için URL
    path('delete_customer/<int:customer_id>/', views.delete_customer, name='delete_customer'),  # Silme URL'si
    path('admin_dashboard/add-customer/', views.add_customer, name='add_customer'),
    path('generate_random_customers/', views.generate_random_customers, name='generate_random_customers'),
    path('delete_all_customers/', views.delete_all_customers, name='delete_all_customers'),
    path('admin_dashboard/add-product/', views.add_product, name='add_product'),
    path('admin_dashboard/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin_dashboard/update-stock/<int:product_id>/', views.update_stock, name='update_stock'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('view_cart/', views.view_cart, name='view_cart'),

    # Tüm kullanıcıları silme URL'si

    # Diğer URL desenleri...

]
