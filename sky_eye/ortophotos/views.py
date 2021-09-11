"""Ortophotos views."""

# Django REST Framework
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action

# Permissions
from rest_framework.permissions import IsAuthenticated

# Models
from sky_eye.ortophotos.models import Ortophoto, Report

# Serializers
from sky_eye.ortophotos.serializers import (OrtoModelSerializer, 
                                            SaveOrtoSerializer,
                                            ReportModelSerializer,
                                            CreateReportSerializer)

# Utils
import os
from pathlib import Path

class OrtoViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """Ortophoto view set."""

    serializer_class = OrtoModelSerializer
    queryset = Ortophoto.objects.all()

    def get_permissions(self):
        """Assign permissions"""

        permissions = [IsAuthenticated]

        return [p() for p in permissions]

    def create(self, request, *args, **kwargs):
        """Handle ortophoto creation"""

        serializer = SaveOrtoSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        ortophoto = serializer.save()
        
        data = self.get_serializer(ortophoto).data

        return Response(data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Add the function of destroying 
        ortophoto on media file
        """

        photo_url = self.queryset.get(pk=kwargs['pk']).photo.url

        path = Path(__file__).resolve(strict=True).parent.parent

        os.remove(str(path)+photo_url)

        return super().destroy(request, *args, **kwargs)


class ReportViewSet(mixins.RetrieveModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """Report view set."""

    serializer_class = ReportModelSerializer
    queryset = Report.objects.all()

    def dispatch(self, request, *args, **kwargs):
        """Verify that the Ortophoto exists."""
        photo_id = self.kwargs['id']
        self.photo = get_object_or_404(
            Ortophoto,
            id=photo_id
        )
        return super(ReportViewSet, self).dispatch(request, *args, **kwargs)

    def get_permissions(self):
        """Assign permission according 
        to action."""

        permissions = [IsAuthenticated]

        return [p() for p in permissions]

    @action(detail=False, methods=['post'])
    def newreport(self, request, *args, **kwargs):
        """Handle report creation."""
        serializer = CreateReportSerializer(
            data = request.data,
            context = {
                'photo': self.photo,
                'user': request.user
                },
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        data = {'message': 'Estamos procesando la ortofoto y te enviaremos un mail al finalizar'}

        return Response(data, status=status.HTTP_200_OK)