"""User models."""

# Django
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """Default user for Sky-eye."""

    email = models.EmailField(
        'email.address',
        unique = True,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )
    
    phone_regex = RegexValidator(
        regex = r'\+?1?\d{9,15}$',
        message = "Phone number must be entered in the format: +999999999. Up to 15 digits allowed."
    )
    
    phone_number = models.CharField(
        validators = [phone_regex],
        max_length = 17,
        blank = True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    is_verified = models.BooleanField(
        'verified',
        default = False,
        help_text= 'Set to true when the user had verified the email address.'
    )

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    