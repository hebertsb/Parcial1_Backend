from typing import Literal, Any
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.decorators import action
from .serializers import MantenimientoSerializer, TareaMantenimientoSerializer
from core.models.propiedades_residentes import Mantenimiento, TareaMantenimiento
from django.utils import timezone

class IsAdminOrUser(BasePermission):
    """
    Permiso para permitir que los administradores tengan acceso completo
    y que los propietarios/inquilinos puedan ver los mantenimientos solicitados
    y los mantenimientos creados por el admin.
    """
    
    def has_permission(self, request, view):  # type: ignore
        # Solo el admin puede editar, borrar o actualizar
        if request.user.is_staff:  # Admin tiene acceso completo
            return True
        # Los propietarios o inquilinos pueden ver sus solicitudes y los mantenimientos del admin
        if view.action == 'list' or view.action == 'retrieve':
            return True
        return False

# Vista para gestionar los mantenimientos
class MantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los mantenimientos.
    """
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer

    def get_permissions(self):
        """
        Controlamos los permisos en función de la acción.
        """
        if self.action == 'create':
            return [IsAuthenticated()]  # Todos los usuarios autenticados pueden crear
        if self.action in ['update', 'destroy']:
            return [IsAdminUser()]  # Solo el admin puede editar o eliminar mantenimientos
        return super().get_permissions()

    def get_queryset(self):  # type: ignore
        """
        Devuelve todos los mantenimientos si el usuario es admin.
        Los propietarios e inquilinos solo verán sus propios mantenimientos y los creados por el admin.
        """
        user = self.request.user
        if user.is_staff:  # Si es admin, puede ver todos los mantenimientos
            return Mantenimiento.objects.all()
        else:  # Los propietarios e inquilinos ven solo los mantenimientos que han solicitado
            return Mantenimiento.objects.filter(
                creado_por=user  # Filtra por el campo 'creado_por' que indica quién lo solicitó
            )

    def perform_create(self, serializer):
        """Realiza la creación de un mantenimiento y lo asigna al usuario que lo solicitó"""
        user = self.request.user
        # Asignar al usuario autenticado como el creador
        serializer.save(creado_por=user)

    @action(detail=True, methods=['post'])
    def cerrar(self, request, pk=None):
        """Cerrar un mantenimiento y cambiar su estado a 'completado'."""
        mantenimiento = self.get_object()
        if mantenimiento.estado != 'en_progreso':
            return Response({'error': 'La tarea debe estar en progreso antes de cerrarla.'}, status=status.HTTP_400_BAD_REQUEST)
        
        mantenimiento.estado = 'completado'
        mantenimiento.fecha_realizacion = timezone.now().date()
        mantenimiento.save()

        return Response({'message': 'Mantenimiento cerrado correctamente.'}, status=status.HTTP_200_OK)


# Vista para gestionar las tareas de mantenimiento
class TareaMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las tareas de mantenimiento.
    """
    queryset = TareaMantenimiento.objects.all()
    serializer_class = TareaMantenimientoSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Definir permisos según la acción realizada.
        """
        if self.action == 'create':
            return [IsAuthenticated()]  # Todos los usuarios autenticados pueden crear tareas
        if self.action in ['update', 'destroy']:
            return [IsAdminUser()]  # Solo el admin puede modificar o eliminar tareas
        return super().get_permissions()

    def perform_create(self, serializer):
        """Crear tarea de mantenimiento y asignar responsable"""
        user = self.request.user
        # Al crear la tarea, asignamos el responsable si el usuario no es admin
        serializer.save(asignado_a=user)

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marcar una tarea como completada."""
        tarea = self.get_object()
        tarea.estado = 'finalizada'
        tarea.save()

        # Verificar si todas las tareas asociadas al mantenimiento están finalizadas
        mantenimiento = tarea.mantenimiento  # Accedemos al mantenimiento asociado
        tareas = TareaMantenimiento.objects.filter(mantenimiento=mantenimiento)
        
        if all(t.estado == 'finalizada' for t in tareas):
            # Si todas las tareas están finalizadas, cambiamos el estado del mantenimiento
            mantenimiento.estado = 'completado'
            mantenimiento.save()

        return Response({'message': 'Tarea completada y mantenimiento actualizado.'}, status=status.HTTP_200_OK)
