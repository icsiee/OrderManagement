from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Django'nun varsayılan URL'lerini kullanma
    path('', include('orders.urls')),  # `orders` app'inizin URLs'ini dahil et
]
