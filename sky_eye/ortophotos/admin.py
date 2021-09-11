"""Ortophoto admin."""

# Django
from django.contrib import admin

# Models
from sky_eye.ortophotos.models import Ortophoto

@admin.register(Ortophoto)
class OrtoAdmin(admin.ModelAdmin):
    """Ortophoto admin."""

    list_display = (
        'photo',
        'description',
        'user'
    )

    search_fields = ('photo',)
