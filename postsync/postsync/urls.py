from django.contrib import admin
from django.urls import path,include
from core.views import contact, index
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('item/',include('item.urls')),
    path('admin/', admin.site.urls),
    path('', index, name='index'),
    path('contact/', contact, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
