from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from api_integration import views
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('api_integration/', include('api_integration.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
