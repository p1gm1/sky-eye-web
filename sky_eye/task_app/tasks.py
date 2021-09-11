"""Celery tasks."""

# Django
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.conf import settings 

# Celery
from celery.decorators import task 

# Models
from sky_eye.users.models import User
from sky_eye.ortophotos.models import Report 

# Rasterio
import rasterio

# Utils
from sky_eye.ortophotos.utils import make_ndvi, count_crops

# Utilities
from datetime import timedelta
import jwt


def _gen_verification_token(user):
    """Create JwT token that the user can
    use to verify the account.
    """

    exp_date = timezone.now() + timedelta(days=3)
    payload = {
        'user': user.username,
        'exp': int(exp_date.timestamp()),
        'type': 'email_confirmation'
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token.decode()

@task(name='send_confimation_email', max_retires=3)
def send_confirmation_email(user_pk):
    """Send confirmation email to
    verify account.
    """

    user = User.objects.get(pk=user_pk)

    verification_token = _gen_verification_token(user)

    subject = f'Bienvenido @{user.username}! Verifica tu cuenta para empezar a usar Sky-eye.'
    from_email = 'Sky eye <noreplay@aisky_skyeye.com>'
    to = user.email
    content = render_to_string(
        'emails/users/account_verification.html',
        context = {
            'token': verification_token,
            'user': user
        }
    )
    msg = EmailMultiAlternatives(
        subject = subject,
        body = content,
        from_email = from_email,
        to = [to]
    )
    msg.attach_alternative(content, "text/html")
    msg.send()

@task(name='create_report', max_retries=3)
def create_report(photo, ndvi, user):
    """Creates report and send
    confirmation mail of the creation.
    """
    crops_url, len_crops = count_crops(photo.photo.url)

    if ndvi:
       ds=rasterio.open(photo.photo.url) 
       band_red=ds.read_band(3)
       band_nir=ds.read_band(4)

       ndvi_photo = make_ndvi(band_NIR=band_nir, band_red=band_red, im=ds)
        
       Report.objects.create(photo=photo,
                             ndvi=ndvi,
                             ndvi_photo=ndvi_photo,
                             crops=len_crops,
                             crops_csv=crops_url)
    else:
        Report.objects.create(photo=photo,
                              crops=len_crops,
                              crops_csv=crops_url)

    subject = f"{user.username} El reporte de tu foto ha sido creado con exito"
    from_email = "Sky eye <noreplay@aisky_skyeye.com>"
    to = user.email

    content = render_to_string(
        'emails/reports/report_creation_verification.html',
        context = {
            'user': user
        }
    )
    msg = EmailMultiAlternatives(
        subject = subject,
        body = content,
        from_email = from_email,
        to = [to]
    )
    msg.attach_alternative(content, "text/html")
    msg.send()