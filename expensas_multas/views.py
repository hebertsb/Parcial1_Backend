
import firebase_admin
from firebase_admin import credentials, messaging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status

# Inicializa firebase-admin solo una vez
import os
FIREBASE_CRED_PATH = r'D:/ParcialBackend/Parcial_1/parcial-aee35-d3ddb4b24d21.json'
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CRED_PATH)
    firebase_admin.initialize_app(cred)

def send_push_fcm_v1(token, title, body):
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=token,
    )
    response = messaging.send(message)
    return response

@api_view(['POST'])
@permission_classes([IsAdminUser])
def enviar_alerta_expensa_vencida(request):
    """
    Endpoint para enviar notificación push de expensa vencida a un usuario.
    Requiere: token_fcm, mensaje
    Solo admin puede usarlo.
    """
    token_fcm = request.data.get('token_fcm')
    mensaje = request.data.get('mensaje', 'Tiene expensas vencidas. Si no paga, perderá beneficios.')
    if not token_fcm:
        return Response({'error': 'Falta token_fcm'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        resultado = send_push_fcm_v1(token_fcm, 'Alerta de Expensa', mensaje)
        return Response({'resultado': resultado})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
    @action(detail=False, methods=['get'], url_path='alerta-vencidas')
    def alerta_expensas_vencidas(self, request):
        """
        Endpoint para que el móvil consulte expensas vencidas/no pagadas y reciba una advertencia de pérdida de beneficios.
        Devuelve expensas con estado 'vencida' o 'morosa' asociadas al usuario autenticado.
        """
        user = request.user
        expensas_vencidas = ExpensasMensuales.objects.filter(
            vivienda__persona=user.persona,
            estado__in=['vencida', 'morosa']
        )
        serializer = self.get_serializer(expensas_vencidas, many=True)
        advertencia = "Tiene expensas vencidas o morosas. Si no realiza el pago, se le quitarán beneficios como uso de áreas comunes y reservas."
        return Response({
            "alerta": True,
            "mensaje": advertencia,
            "expensas": serializer.data
        })
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

 