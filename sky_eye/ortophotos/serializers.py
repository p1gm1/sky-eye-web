"""Ortophoto Serializer."""

# Django REST framework
from rest_framework import serializers

# Serializer
from sky_eye.users.serializers import UserModelSerializer

# Model
from sky_eye.ortophotos.models import Ortophoto, Report

# Tasks
from sky_eye.task_app.tasks import create_report

# Threads
import threading


class CountCropsThread(threading.Thread):
    """New thread that counts
    crops and makes ndvi
    """
    def __init__(self, photo, ndvi, user, lock, *args, **kwargs):
        self.photo = photo
        self.ndvi = ndvi
        self.user = user
        self.lock = lock
        super(CountCropsThread, self).__init__(*args, **kwargs)
    
    def run(self):

        self.lock.acquire(True)
        create_report(self.photo, self.ndvi, self.user)
        self.lock.release()


class OrtoModelSerializer(serializers.ModelSerializer):
    """Orto model serializer."""

    user = UserModelSerializer(read_only=True)

    class Meta:
        """Meta properties."""
        model = Ortophoto
        fields = ('user' ,'photo', 'description')

        read_only_fields = (
            'user',
        )


class SaveOrtoSerializer(serializers.Serializer):
    """Saves ortophoto uploaded
    in media file.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    photo = serializers.FileField()
    description = serializers.CharField(max_length=55)

    def create(self, data):
        """Handle the photo save action."""
        
        if not data['user']:
            user = self.context['request'].user
        else:
            user = data.pop('user')

        ortophoto = Ortophoto.objects.create(
            user=user,
            photo=data['photo'],
            description=data['description']
        )

        return ortophoto 


class ReportModelSerializer(serializers.Serializer):
    """Report model serializer."""

    photo = OrtoModelSerializer(read_only=True)
    crops_csv = serializers.CharField(max_length=55)
    ndvi_photo = serializers.FileField()

    class Meta:
        """Meta Properties."""
        model = Report
        fields = ('photo', 'crops_csv', 'ndvi_photo')

        read_only_fields = (
            'photo'
        )


class CreateReportSerializer(serializers.Serializer):
    """Handles creation of
    report.
    """

    ndvi = serializers.BooleanField()

    def validate(self, data):
        """Verify data is valid"""
        
        try:
            assert type(data['ndvi']) == bool
        except AssertionError:
            raise serializers.ValidationError('Invalid NDVI data')

        self.context['ndvi'] = data['ndvi'] 

        return data

    def save(self):
        """Handle the report creation."""

        photo = self.context['photo']
        ndvi = self.context['ndvi']
        user = self.context['user']

        lock = threading.Lock()
        CountCropsThread(photo, ndvi, user, lock).start()

