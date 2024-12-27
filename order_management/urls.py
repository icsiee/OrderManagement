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

# orders/urls.py

from django.urls import path
from . import consumers
from django.urls import re_path

# WebSocket yolunu consumer'a yönlendir
websocket_urlpatterns = [
    re_path(r'ws/orders/$', consumers.OrderConsumer.as_asgi()),
]
