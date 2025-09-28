from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ExpensasMensualesSerializer
from core.serializers import RegistrarPagoSerializer
from core.models.propiedades_residentes import ExpensasMensuales
from core.models.administracion import Pagos
from core.services.payments import total_pagado_expensa
from decimal import Decimal
from rest_framework.decorators import action

class ExpensasMensualesViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones sobre las expensas mensuales.
    El Administrador puede hacer CRUD completo.
    Los Propietarios e Inquilinos solo pueden ver sus expensas y realizar pagos.
    """
    queryset = ExpensasMensuales.objects.all()
    serializer_class = ExpensasMensualesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filtrar las expensas de acuerdo al usuario.
        Los Administradores pueden ver todas las expensas.
        Los Propietarios/Inquilinos solo pueden ver sus expensas.
        """
        user = self.request.user
        if user.is_staff:  # Si es administrador
            return ExpensasMensuales.objects.all()
        else:  # Si es propietario o inquilino
            return ExpensasMensuales.objects.filter(vivienda__propiedad__persona=user.persona)

    def perform_create(self, serializer):
        """
        Solo el administrador puede crear nuevas expensas mensuales.
        """
        if self.request.user.is_staff:
            serializer.save()

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        """
        Permite a un propietario o inquilino pagar una expensa.
        Crea un registro en la tabla de pagos y actualiza el estado de la expensa.
        """
        expensa = self.get_object()  # Obtiene la expensa correspondiente a la ID

        # Solo el propietario o inquilino puede pagar una expensa asociada a su vivienda
        if expensa.vivienda.propiedad.persona != request.user.persona:
            return Response({'error': 'No tienes permiso para pagar esta expensa.'}, status=status.HTTP_403_FORBIDDEN)

        # Verifica el monto de la expensa pendiente
        total_pagado = total_pagado_expensa(expensa)
        monto_pendiente = max(Decimal('0.00'), expensa.monto_total - total_pagado)

        # Verifica que el monto enviado sea válido
        monto_pago = request.data.get('monto')
        if monto_pago > monto_pendiente:
            return Response({'error': 'El monto excede el saldo pendiente.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if monto_pago <= 0:
            return Response({'error': 'El monto debe ser mayor a cero.'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear el pago
        payment_data = {
            'persona': request.user.persona,
            'tipo_pago': 'expensa',
            'expensa': expensa.id,
            'monto': monto_pago,
            'metodo_pago': request.data.get('metodo_pago', 'tarjeta'),
        }

        # Registrar el pago
        serializer = RegistrarPagoSerializer(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            # Después de registrar el pago, actualizamos el estado de la expensa
            total_pagado = total_pagado_expensa(expensa)
            if total_pagado >= expensa.monto_total:
                expensa.estado = 'pagada'
            else:
                expensa.estado = 'parcial'
            expensa.save()
            return Response({'message': 'Pago registrado correctamente.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
