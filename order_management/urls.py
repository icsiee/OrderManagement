from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Django'nun varsayılan URL'lerini kullanma
    path('', include('orders.urls')),  # `orders` app'inizin URLs'ini dahil et
    path('admin_dashboard/', include('orders.urls')),  # Custom admin paneli

]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
