from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('produtos/', include('product.urls')),
    path('pedidos/', include('order.urls')),
    path('perfil/', include('account.urls')),
]

# use 127.0.0.1:8000 to access the server from host machine
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)