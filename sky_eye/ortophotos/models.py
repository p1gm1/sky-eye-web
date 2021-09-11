"""Orto models"""

# Django
from django.db import models 
from django.utils.translation import gettext_lazy as _

# Models
from sky_eye.users.models import User

class Ortophoto(models.Model):
    """Ortophoto model for Sky-eye"""

    photo = models.FileField(_("Ortofoto"),
                             upload_to='ortophoto/pictures',
                             blank=True,
                             null=True)
    description = models.TextField(_("Descripcion"),
                                   max_length=500,
                                   blank=True,
                                   null=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name=_("Registrado por"))

    def __str__(self):
        return '{}'.format(self.pk)


class Report(models.Model):
    """Reports model for Sky-eye"""
    photo = models.OneToOneField(Ortophoto, 
                                 on_delete=models.CASCADE,
                                 verbose_name=_("Ortofoto"))
    ndvi = models.BooleanField(_("Indice NDVI"),
                               default=False)
    ndvi_photo = models.FileField(_("NDVI foto"),
                                  upload_to='ortophoto/pictures/ndvi',
                                  blank=True,
                                  null=True)
    crops = models.IntegerField(_("Conteo de objetos"),
                                default=0)
    crops_csv = models.CharField(_("CSV Coordendas"),
                                 max_length=150,
                                 blank=True,
                                 null=True)

    def __str__(self):
        return '{}'.format(self.pk)
