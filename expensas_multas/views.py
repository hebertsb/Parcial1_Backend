from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ExpensasMensualesSerializer
from core.serializers import RegistrarPagoSerializer
from core.models.propiedades_residentes import ExpensasMensuales, Propiedad
from core.services.payments import total_pagado_expensa
from decimal import Decimal, InvalidOperation
from rest_framework.decorators import action

class ExpensasMensualesViewSet(viewsets.ModelViewSet):
    queryset = ExpensasMensuales.objects.all()
    serializer_class = ExpensasMensualesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ExpensasMensuales.objects.all()
        else:
            return ExpensasMensuales.objects.filter(vivienda__persona=user.persona)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            serializer.save()

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        expensa = self.get_object()
        if expensa.vivienda.persona != request.user.persona:
            return Response({'error': 'No tienes permiso para pagar esta expensa.'}, status=status.HTTP_403_FORBIDDEN)

        total_pagado = total_pagado_expensa(expensa)
        monto_pendiente = max(Decimal('0.00'), expensa.monto_total - total_pagado)

        try:
            monto_pago = Decimal(request.data.get('monto', '0'))
        except Exception:
            return Response({'error': 'Monto inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if monto_pago > monto_pendiente:
            return Response({'error': 'El monto excede el saldo pendiente.'}, status=status.HTTP_400_BAD_REQUEST)
        if monto_pago <= 0:
            return Response({'error': 'El monto debe ser mayor a cero.'}, status=status.HTTP_400_BAD_REQUEST)

        payment_data = {
            'persona': request.user.persona,
            'tipo': 'expensa',
            'objetivo_id': expensa.id,
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
            total_pagado = total_pagado_expensa(expensa)
            expensa.estado = 'pagada' if total_pagado >= expensa.monto_total else 'parcial'
            expensa.save(update_fields=['estado'])
            return Response({'message': 'Pago registrado correctamente.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 