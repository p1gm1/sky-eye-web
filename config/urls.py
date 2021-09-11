from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("", include(("sky_eye.users.urls", 'users'), namespace="users")),
    path("", include(("sky_eye.ortophotos.urls", 'ortophotos'), namespace="ortophotos"))
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)