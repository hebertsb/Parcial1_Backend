from __future__ import annotations

from decimal import Decimal
from django.db.models import Q, Sum
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from core.models.propiedades_residentes import ReservaEspacio
from core.models.administracion import Pagos
from core.services.payments import total_pagado_reserva
from core.serializers import RegistrarPagoSerializer
from reservas_areas.serializers import ReservaEspacioSerializer

class ReservaEspacioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las reservas de espacios comunes.
    """
    serializer_class = ReservaEspacioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtra las reservas para que cada usuario solo vea sus propias reservas.
        Si el usuario es un administrador, verá todas las reservas.
        """
        user = self.request.user
        if not user.is_authenticated or not hasattr(user, 'persona'):
            return ReservaEspacio.objects.none()

        if user.is_staff:  # Verificar si el usuario es administrador
            return ReservaEspacio.objects.all()  # Devolver todas las reservas para los administradores

        return ReservaEspacio.objects.filter(persona=user.persona)  # El usuario normal ve solo sus reservas

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

        # Solo se puede confirmar si no está confirmada previamente
        if reserva.estado == 'confirmada':
            return Response({'message': 'La reserva ya está confirmada.'}, status=status.HTTP_400_BAD_REQUEST)

        reserva.estado = 'confirmada'
        reserva.fecha_confirmacion = timezone.now()
        reserva.save()
        return Response({'message': 'Reserva confirmada correctamente.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def registrar_pago(self, request, pk=None):
        """Registrar el pago asociado a la reserva."""
        reserva = self.get_object()

        # No es necesario confirmar nuevamente la reserva si ya está confirmada
        if reserva.estado == 'cancelada':
            return Response({'error': 'La reserva ha sido cancelada.'}, status=status.HTTP_400_BAD_REQUEST)

        if reserva.estado != 'confirmada':
            return Response({'error': 'La reserva debe estar confirmada antes de registrar el pago.'}, status=status.HTTP_400_BAD_REQUEST)

        # Calcular el monto pendiente
        total_pagado = Pagos.objects.filter(reserva=reserva).aggregate(total_pagado=Sum('monto'))['total_pagado'] or Decimal('0.00')
        monto_pendiente = max(Decimal('0.00'), reserva.monto_total - total_pagado)

        try:
            monto_pago = Decimal(request.data.get('monto', '0'))
        except Exception:
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if monto_pago > monto_pendiente:
            return Response({'error': 'El monto excede el saldo pendiente.'}, status=status.HTTP_400_BAD_REQUEST)
        if monto_pago <= 0:
            return Response({'error': 'El monto debe ser mayor a cero.'}, status=status.HTTP_400_BAD_REQUEST)

        # Serializa y guarda el pago
        payment_data = {
            'tipo': 'reserva',
            'objetivo_id': reserva.id,
            'monto': monto_pago,
            'metodo_pago': request.data.get('metodo_pago', 'tarjeta'),
            'referencia': request.data.get('referencia', ''),
        }

        serializer = RegistrarPagoSerializer(
            data=payment_data,
            context={'persona': request.user.persona, 'request': request}
        )

        if serializer.is_valid():
            serializer.save()

            # Verificar el total pagado y actualizar el estado de la reserva
            total_pagado = Pagos.objects.filter(reserva=reserva).aggregate(total_pagado=Sum('monto'))['total_pagado'] or Decimal('0.00')
            reserva.estado = 'pagada' if total_pagado >= reserva.monto_total else 'parcial'
            reserva.fecha_pago = timezone.now()
            reserva.save()

            return Response({'message': 'Pago registrado correctamente.'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancelar_reserva(self, request, pk=None):
        """Cancelar una reserva y actualizar el estado."""
        reserva = self.get_object()
        reserva.estado = 'cancelada'
        reserva.save()
        return Response({'message': 'Reserva cancelada correctamente.'}, status=status.HTTP_200_OK)
