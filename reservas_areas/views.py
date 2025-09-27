from django.db.models import Q, F
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ReservaEspacioSerializer
from core.models.propiedades_residentes import ReservaEspacio
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError

class ReservaEspacioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las reservas de espacios comunes.
    """
    serializer_class = ReservaEspacioSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtra las reservas para que cada usuario solo vea sus propias reservas.
        """
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'persona'):
            return ReservaEspacio.objects.none()
        return ReservaEspacio.objects.filter(persona=user.persona)
    
    def perform_create(self, serializer):
        """
        Se realiza la creación de la reserva, asegurando que solo se cree si el usuario es válido.
        Además, se verifica que no exista una reserva en el mismo rango de fecha y hora.
        """
        user = self.request.user
        fecha_reserva = serializer.validated_data['fecha_reserva']
        hora_inicio = serializer.validated_data['hora_inicio']
        hora_fin = serializer.validated_data['hora_fin']
        espacio_comun = serializer.validated_data['espacio_comun']
        
        # Validación: comprobar si hay superposición de horarios
        reserva_conflictiva = ReservaEspacio.objects.filter(
            espacio_comun=espacio_comun,
            fecha_reserva=fecha_reserva,
        ).filter(
            Q(hora_inicio__lt=hora_fin) & Q(hora_fin__gt=hora_inicio)
        ).exists()
        
        if reserva_conflictiva:
            raise ValidationError("La reserva no se puede realizar, el horario ya está ocupado.")
        
        # Si no hay conflicto, guardamos la reserva
        if not user.is_authenticated or not hasattr(user, 'persona'):
            raise ValidationError("El usuario no tiene persona asociada.")
        serializer.save(persona=getattr(user, 'persona', None), fecha_solicitud=timezone.now())
        return super().perform_create(serializer)

    @action(detail=True, methods=['post'])
    def confirmar_reserva(self, request, pk=None):
        """Confirmar la reserva y cambiar el estado a 'confirmada'."""
        reserva = self.get_object()
        reserva.estado = 'confirmada'
        reserva.fecha_confirmacion = timezone.now()
        reserva.save()
        return Response({'message': 'Reserva confirmada correctamente.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        """Registrar el pago asociado a la reserva."""
        reserva = self.get_object()
        if reserva.estado != 'confirmada':
            return Response({'error': 'La reserva debe estar confirmada antes de registrar el pago.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualiza el estado a 'pagada'
        reserva.estado = 'pagada'
        reserva.fecha_pago = timezone.now()
        reserva.save()
        
        return Response({'message': 'Pago registrado correctamente.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def cancelar_reserva(self, request, pk=None):
        """Cancelar una reserva y actualizar el estado."""
        reserva = self.get_object()
        reserva.estado = 'cancelada'
        reserva.save()
        return Response({'message': 'Reserva cancelada correctamente.'}, status=status.HTTP_200_OK)
