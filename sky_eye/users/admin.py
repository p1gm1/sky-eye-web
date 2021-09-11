from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    list_display = ('email', 
                    'username', 
                    'first_name', 
                    'last_name',
                    'is_staff',
    )

    list_filter = ('is_staff',)
