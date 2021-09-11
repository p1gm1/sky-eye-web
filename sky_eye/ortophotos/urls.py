"""Ortophotos urls"""

# Django
from posixpath import basename
from django.urls import path, include

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from sky_eye.ortophotos.views import OrtoViewSet, ReportViewSet

router = DefaultRouter()
router.register(
    r'ortophotos', 
    OrtoViewSet, 
    basename='ortophotos'
)
router.register(
    r'ortophotos/(?P<id>[a-zA-Z0-9_-]+)/reports', 
    ReportViewSet, 
    basename='reports'
)

urlpatterns = [
    path('', include(router.urls))
]