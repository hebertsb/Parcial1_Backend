from rest_framework import generics, permissions
from core.models.administracion import BitacoraAcciones, LogSistema
from .serializers import BitacoraAccionesSerializer, LogSistemaSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff

class BitacoraAccionesListView(generics.ListAPIView):
    queryset = BitacoraAcciones.objects.all().order_by('-fecha_hora')
    serializer_class = BitacoraAccionesSerializer
    permission_classes = [IsAdminUser]

class LogSistemaListView(generics.ListAPIView):
    queryset = LogSistema.objects.all().order_by('-fecha_hora')
    serializer_class = LogSistemaSerializer
    permission_classes = [IsAdminUser]
