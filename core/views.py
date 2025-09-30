from typing import cast
from decimal import Decimal, InvalidOperation

from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.models.administracion import Pagos
from core.serializers import (
    ExpensaDebtSerializer,
    MultaDebtSerializer,
    PagoDetailSerializer,
    PersonaResumenSerializer,
    RegistrarPagoSerializer,
)
from core.services.payments import (
    CONFIRMED_PAYMENT_STATES,
    crear_expensa_demo,
    crear_multa_demo,
    ensure_persona_for_user,
    expensas_pendientes,
    get_persona_for_user,
    multas_pendientes,
)


class PendingDebtsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        persona = get_persona_for_user(request.user)
        if not persona:
            return Response(
                {'detail': 'No se encontro un perfil de persona asociado al usuario autenticado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        expensas_qs = expensas_pendientes(persona)
        multas_qs = multas_pendientes(persona)

        pagos_expensas = (
            Pagos.objects
            .filter(expensa__in=expensas_qs, estado__in=CONFIRMED_PAYMENT_STATES)
            .values('expensa_id')
            .annotate(total=Sum('monto'))
        )
        pagos_multa = (
            Pagos.objects
            .filter(multa__in=multas_qs, estado__in=CONFIRMED_PAYMENT_STATES)
            .values('multa_id')
            .annotate(total=Sum('monto'))
        )
        pagos_por_expensa = {item['expensa_id']: item['total'] or Decimal('0') for item in pagos_expensas}
        pagos_por_multa = {item['multa_id']: item['total'] or Decimal('0') for item in pagos_multa}

        expensas_data = ExpensaDebtSerializer(
            expensas_qs,
            many=True,
            context={'pagos_por_expensa': pagos_por_expensa},
        ).data
        multas_data = MultaDebtSerializer(
            multas_qs,
            many=True,
            context={'pagos_por_multa': pagos_por_multa},
        ).data

        total_expensas = sum(Decimal(str(item['monto_pendiente'])) for item in expensas_data)
        total_multas = sum(Decimal(str(item['monto_pendiente'])) for item in multas_data)

        return Response({
            'persona': PersonaResumenSerializer(persona).data,
            'expensas': expensas_data,
            'multas': multas_data,
            'resumen': {
                'total_pendiente': total_expensas + total_multas,
                'total_expensas_pendientes': total_expensas,
                'total_multas_pendientes': total_multas,
                'cantidad_expensas': len(expensas_data),
                'cantidad_multas': len(multas_data),
            },
        })


class RegistrarPagoView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        persona = get_persona_for_user(request.user)
        if not persona:
            return Response(
                {'detail': 'No se encontro un perfil de persona asociado al usuario autenticado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = RegistrarPagoSerializer(
            data=request.data,
            context={'persona': persona, 'request': request},
        )
        serializer.is_valid(raise_exception=True)
        pago = cast(Pagos, serializer.save())

        payload = {
            'pago': PagoDetailSerializer(pago).data,
        }

        if pago.expensa:
            total_pagado_expensa = (
                Pagos.objects
                .filter(expensa=pago.expensa, estado__in=CONFIRMED_PAYMENT_STATES)
                .aggregate(total=Sum('monto'))['total'] or Decimal('0')
            )
            expensa_serializer = ExpensaDebtSerializer(
                [pago.expensa],
                many=True,
                context={'pagos_por_expensa': {pago.expensa.id: total_pagado_expensa}},
            )
            payload['expensa_actualizada'] = expensa_serializer.data[0]

        if pago.multa:
            total_pagado_multa = (
                Pagos.objects
                .filter(multa=pago.multa, estado__in=CONFIRMED_PAYMENT_STATES)
                .aggregate(total=Sum('monto'))['total'] or Decimal('0')
            )
            multa_serializer = MultaDebtSerializer(
                [pago.multa],
                many=True,
                context={'pagos_por_multa': {pago.multa.id: total_pagado_multa}},
            )
            payload['multa_actualizada'] = multa_serializer.data[0]

        # Agregar manejo de reservas
        if hasattr(pago, 'reserva') and pago.reserva:
            from core.services.payments import total_pagado_reserva
            total_pagado_reserva_actual = total_pagado_reserva(pago.reserva)
            payload['reserva_actualizada'] = {
                'id': pago.reserva.id,
                'monto_total': pago.reserva.monto_total,
                'monto_pagado': total_pagado_reserva_actual,
                'monto_pendiente': max(Decimal('0'), pago.reserva.monto_total - total_pagado_reserva_actual),
                'estado': 'pagada' if total_pagado_reserva_actual >= pago.reserva.monto_total else 'parcial'
            }

        return Response(payload, status=status.HTTP_201_CREATED)


class DemoDebtsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        persona = ensure_persona_for_user(request.user)
        try:
            cantidad_expensas = int(request.data.get('cantidad_expensas', 1) or 1)
            cantidad_multas = int(request.data.get('cantidad_multas', 1) or 1)
        except (TypeError, ValueError):
            return Response({'detail': 'Los campos cantidad_expensas y cantidad_multas deben ser enteros.'}, status=status.HTTP_400_BAD_REQUEST)
        cantidad_expensas = max(cantidad_expensas, 1)
        cantidad_multas = max(cantidad_multas, 1)
        try:
            monto_expensa = Decimal(str(request.data.get('monto_expensa', '450.00')))
            monto_multa = Decimal(str(request.data.get('monto_multa', '150.00')))
        except InvalidOperation:
            return Response({'detail': 'Los montos deben ser valores numericos validos.'}, status=status.HTTP_400_BAD_REQUEST)

        expensas_creadas = [crear_expensa_demo(persona, monto_expensa) for _ in range(cantidad_expensas)]
        multas_creadas = [crear_multa_demo(persona, monto_multa) for _ in range(cantidad_multas)]

        expensas_data = ExpensaDebtSerializer(
            expensas_creadas,
            many=True,
            context={'pagos_por_expensa': {}},
        ).data
        multas_data = MultaDebtSerializer(
            multas_creadas,
            many=True,
            context={'pagos_por_multa': {}},
        ).data

        return Response({
            'detail': 'Datos demo generados correctamente.',
            'persona': PersonaResumenSerializer(persona).data,
            'expensas_creadas': expensas_data,
            'multas_creadas': multas_data,
        }, status=status.HTTP_201_CREATED)



