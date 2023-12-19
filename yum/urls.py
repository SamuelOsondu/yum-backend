from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path

from yum import settings

urlpatterns = [
    re_path(r'^chaining/', include('smart_selects.urls')),
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),
    path('vendor/', include('vendor.urls')),
    path('billing/', include('billing.urls')),
    path('food/', include('food.urls')),
    path('manager/', include('manager.urls')),
    path("auth/", include('djoser.urls')),
    path("auth/", include('djoser.urls.jwt')),
    path("auth/", include("djoser.social.urls")),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

