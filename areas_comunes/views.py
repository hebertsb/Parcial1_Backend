from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import EspacioComunSerializer, DisponibilidadEspacioComunSerializer
from core.models.propiedades_residentes import EspacioComun, DisponibilidadEspacioComun


# Permiso personalizado para el Administrador
class IsAdminUser(permissions.BasePermission):
    """
    Permiso para asegurar que solo el Administrador pueda realizar acciones de escritura.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # Permite solo lectura
            return True
        return request.user.is_staff  # Solo el Administrador puede escribir


class EspacioComunViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Espacios Comunes.
    El Administrador puede realizar CRUD completo, los demás solo pueden ver los espacios comunes.
    """

    queryset = EspacioComun.objects.all()
    serializer_class = EspacioComunSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Solo el Admin puede modificar, todos pueden leer

    def get_queryset(self):
        """
        Los usuarios autenticados solo podrán ver los espacios comunes disponibles, los demás no
        """
        user = self.request.user
        if user.is_staff:
            return EspacioComun.objects.all()  # Admin puede ver todo
        return EspacioComun.objects.filter(activo=True)  # Los demás usuarios ven solo los activos


class DisponibilidadEspacioComunViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar la Disponibilidad de los Espacios Comunes.
    El Administrador puede realizar CRUD completo, los demás solo pueden ver la disponibilidad.
    """

    queryset = DisponibilidadEspacioComun.objects.all()
    serializer_class = DisponibilidadEspacioComunSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]  # Solo el Admin puede modificar, todos pueden leer

    def get_queryset(self):
        """
        Los usuarios autenticados solo podrán ver la disponibilidad de los espacios comunes,
        y solo si es para un espacio activo.
        """
        user = self.request.user
        if user.is_staff:
            return DisponibilidadEspacioComun.objects.all()  # Admin puede ver todo
        # Solo mostramos las disponibilidades para los espacios comunes activos
        return DisponibilidadEspacioComun.objects.filter(espacio_comun__activo=True)




