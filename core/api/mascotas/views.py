from typing import Any
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models.propiedades_residentes import Mascota
from .serializers import MascotaSerializer, MascotaDetailSerializer, MascotaListSerializer

class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self) -> Any:
        if self.action == 'list':
            return MascotaListSerializer
        elif self.action == 'retrieve':
            return MascotaDetailSerializer
        return MascotaSerializer