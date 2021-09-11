"""User custom permissions"""

# Django REST framework
from rest_framework.permissions import BasePermission

# Models
from sky_eye.users.models import User

class IsAccountOwner(BasePermission):
    """Allow access only to objects owned
    by the requesting user.
    """

    def has_object_permission(self, request, view, obj):
        """Check object and user are the same."""

        return request.user == obj