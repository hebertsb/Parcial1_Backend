from rest_framework import serializers
from core.models.propiedades_residentes import ReservaEspacio
from authz.models import Persona
from core.models.propiedades_residentes import EspacioComun
from datetime import datetime
from core.models.administracion import Pagos
from core.services.payments import total_pagado_reserva
from core.serializers import RegistrarPagoSerializer, PagoDetailSerializer
from typing import Optional
from django.utils import timezone
from django.db import transaction
from decimal import Decimal



class ReservaEspacioSerializer(serializers.ModelSerializer):
    persona = serializers.PrimaryKeyRelatedField(queryset=Persona.objects.all(), required=False)
    espacio_comun = serializers.PrimaryKeyRelatedField(queryset=EspacioComun.objects.all())
    estado = serializers.ChoiceField(choices=ReservaEspacio.ESTADO_CHOICES, default='solicitada')

    class Meta:
        model = ReservaEspacio
        fields = [
            'id', 'persona', 'espacio_comun', 'fecha_reserva', 'hora_inicio', 'hora_fin',
            'tipo_evento', 'estado', 'monto_total', 'monto_deposito', 'fecha_solicitud',
            'fecha_pago', 'fecha_confirmacion', 'aprobada_por', 'observaciones_cliente',
            'observaciones_admin', 'calificacion_post_uso', 'comentarios_post_uso'
        ]

    def validate_fecha_reserva(self, value):
        # Validación de que la fecha no esté en el pasado
        if value < datetime.today().date():
            raise serializers.ValidationError("La fecha de reserva no puede ser en el pasado.")
        return value


class RegistrarPagoReservaSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=(('reserva', 'reserva')))
    objetivo_id = serializers.IntegerField()
    metodo_pago = serializers.ChoiceField(choices=(
        ('tarjeta', 'tarjeta'),
        ('transferencia', 'transferencia'),
        ('efectivo', 'efectivo'),
    ))
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    referencia = serializers.CharField(max_length=100, allow_blank=True, required=False)

    def validate(self, attrs):
        persona: Optional[Persona] = self.context.get('persona')
        if not persona:
            raise serializers.ValidationError('No se pudo identificar al copropietario asociado al usuario.')

        tipo = attrs['tipo']
        objetivo_id = attrs['objetivo_id']
        metodo_pago = attrs['metodo_pago']
        monto = attrs.get('monto')

        if tipo == 'reserva':
            reserva = ReservaEspacio.objects.filter(
                id=objetivo_id,
                persona=persona,
            ).first()
            if not reserva:
                raise serializers.ValidationError('La reserva indicada no existe o no pertenece al usuario.')

            pendiente = max(Decimal('0'), reserva.monto_total - total_pagado_reserva(reserva))
            if pendiente <= 0:
                raise serializers.ValidationError('La reserva seleccionada ya se encuentra pagada.')
            if monto is None:
                monto = pendiente
            if monto <= 0:
                raise serializers.ValidationError('El monto a pagar debe ser mayor a cero.')
            if monto > pendiente:
                raise serializers.ValidationError('El monto supera el saldo pendiente de la reserva.')

            attrs['reserva'] = reserva
            attrs['monto'] = monto
            attrs['pendiente'] = pendiente - monto

        attrs['metodo_pago'] = metodo_pago
        return attrs

    def create(self, validated_data):
        persona: Persona = self.context['persona']
        usuario = self.context['request'].user
        reserva: Optional[ReservaEspacio] = validated_data.get('reserva')
        monto: Decimal = validated_data['monto']
        metodo_pago: str = validated_data['metodo_pago']
        referencia: str = validated_data.get('referencia') or ''

        referencia_generada = referencia.strip() or timezone.now().strftime('SIM-%Y%m%d%H%M%S')

        with transaction.atomic():
            pago = Pagos.objects.create(
                persona=persona,
                tipo_pago='reserva',
                reserva=reserva,
                monto=monto,
                metodo_pago=metodo_pago,
                numero_comprobante=referencia_generada,
                estado='procesado',
                procesado_por=usuario,
            )

            total_pagado = total_pagado_reserva(reserva)
            reserva.estado = 'pagada' if total_pagado >= reserva.monto_total else 'parcial'
            reserva.save(update_fields=['estado'])

        return pago

    def to_representation(self, instance):
        # Garantiza que siempre se retorna un dict, compatible con DRF
        data = PagoDetailSerializer(instance).data
        if not isinstance(data, dict):
            data = dict(data)
        return data
