from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .serializers import AvisosPersonalizadosSerializer, ComunicadosAdministracionSerializer
from core.models.propiedades_residentes import AvisosPersonalizados, ComunicadosAdministracion

class AvisosPersonalizadosViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Avisos Personalizados.
    """
    serializer_class = AvisosPersonalizadosSerializer
    
    def get_permissions(self):
        """
        Sobrescribimos este método para aplicar permisos personalizados
        """
        user = self.request.user
        
        # Si el usuario es administrador, tiene acceso completo (CRUD)
        if user.is_staff:
            return [IsAuthenticated()]
        
        # Si no es admin, solo puede hacer GET (lectura)
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        # Para cualquier otra acción (post, put, delete) no permitida
        raise PermissionDenied("No tienes permisos para realizar esta acción.")
    
    def get_queryset(self):
        """
        Filtra los avisos personalizados para que solo se muestren aquellos dirigidos
        a la persona que está autenticada, excepto si el usuario tiene rol de admin.
        """
        user = self.request.user
        
        # Admin puede ver todos los avisos
        if user.is_staff:
            return AvisosPersonalizados.objects.all()
        
        # Usuarios comunes pueden ver solo los avisos que les fueron asignados
        return AvisosPersonalizados.objects.filter(persona_destinatario=user.persona)

    @action(detail=True, methods=['post'])
    def enviar(self, request, pk=None):
        """Acción para enviar un aviso personalizado"""
        aviso = self.get_object()
        aviso.estado_envio = 'enviado'
        aviso.fecha_envio = timezone.now()
        aviso.save()
        
        return Response({'message': 'Aviso enviado exitosamente'}, status=status.HTTP_200_OK)


class ComunicadosAdministracionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Comunicados de Administración.
    """
    serializer_class = ComunicadosAdministracionSerializer
    
    def get_permissions(self):
        """
        Sobrescribimos este método para aplicar permisos personalizados
        """
        user = self.request.user
        
        # Si el usuario es administrador, tiene acceso completo (CRUD)
        if user.is_staff:
            return [IsAuthenticated()]
        
        # Si no es admin, solo puede hacer GET (lectura)
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        
        # Para cualquier otra acción (post, put, delete) no permitida
        raise PermissionDenied("No tienes permisos para realizar esta acción.")
    
    def get_queryset(self):
        """
        Filtra los comunicados para que solo se muestren aquellos dirigidos
        a la persona que está autenticada, excepto si el usuario tiene rol de admin.
        """
        user = self.request.user
        
        # Admin puede ver todos los comunicados
        if user.is_staff:
            return ComunicadosAdministracion.objects.all()
        
        # Usuarios comunes pueden ver solo los comunicados dirigidos a ellos
        return ComunicadosAdministracion.objects.filter(dirigido_a__contains=user.persona.id)  # Ajusta la lógica según sea necesario
    
    @action(detail=True, methods=['post'])
    def confirmar_lectura(self, request, pk=None):
        """Acción para confirmar la lectura del comunicado"""
        comunicado = self.get_object()
        comunicado.leido_por.append(request.user.id)  # Guarda el usuario que leyó el comunicado
        comunicado.save()
        
        return Response({'message': 'Lectura confirmada'}, status=status.HTTP_200_OK)
