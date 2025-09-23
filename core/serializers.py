from __future__ import annotations

from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from core.models.administracion import Pagos
from core.models.propiedades_residentes import (
    ExpensasMensuales,
    MultasSanciones,
    Persona,
)
from core.services.payments import (
    total_pagado_expensa,
    total_pagado_multa,
)


class PersonaResumenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = (
            'id',
            'nombre',
            'apellido',
            'email',
            'documento_identidad',
            'tipo_persona',
        )


class ExpensaDebtSerializer(serializers.ModelSerializer):
    vivienda = serializers.SerializerMethodField()
    monto_pagado = serializers.SerializerMethodField()
    monto_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = ExpensasMensuales
        fields = (
            'id',
            'periodo_year',
            'periodo_month',
            'monto_total',
            'estado',
            'monto_pagado',
            'monto_pendiente',
            'vivienda',
        )

    def get_vivienda(self, obj):
        vivienda = obj.vivienda
        return {
            'id': vivienda.id,
            'numero_casa': vivienda.numero_casa,
            'bloque': vivienda.bloque,
            'tipo_vivienda': vivienda.tipo_vivienda,
        }

    def get_monto_pagado(self, obj) -> Decimal:
        pagos_map = self.context.get('pagos_por_expensa')
        if pagos_map is not None:
            return pagos_map.get(obj.id, Decimal('0'))
        return total_pagado_expensa(obj)

    def get_monto_pendiente(self, obj) -> Decimal:
        pagado = self.get_monto_pagado(obj)
        return max(Decimal('0'), obj.monto_total - pagado)


class MultaDebtSerializer(serializers.ModelSerializer):
    tipo_infraccion = serializers.SerializerMethodField()
    monto_pagado = serializers.SerializerMethodField()
    monto_pendiente = serializers.SerializerMethodField()

    class Meta:
        model = MultasSanciones
        fields = (
            'id',
            'descripcion_detallada',
            'monto',
            'estado',
            'fecha_infraccion',
            'tipo_infraccion',
            'monto_pagado',
            'monto_pendiente',
        )

    def get_tipo_infraccion(self, obj):
        infraccion = obj.tipo_infraccion
        return {
            'id': infraccion.id,
            'codigo': infraccion.codigo,
            'nombre': infraccion.nombre,
        }

    def get_monto_pagado(self, obj) -> Decimal:
        pagos_map = self.context.get('pagos_por_multa')
        if pagos_map is not None:
            return pagos_map.get(obj.id, Decimal('0'))
        return total_pagado_multa(obj)

    def get_monto_pendiente(self, obj) -> Decimal:
        pagado = self.get_monto_pagado(obj)
        return max(Decimal('0'), obj.monto - pagado)


class PagoDetailSerializer(serializers.ModelSerializer):
    persona = PersonaResumenSerializer(read_only=True)

    class Meta:
        model = Pagos
        fields = (
            'id',
            'persona',
            'tipo_pago',
            'monto',
            'metodo_pago',
            'numero_comprobante',
            'estado',
            'fecha_pago',
            'expensa_id',
            'multa_id',
        )


class RegistrarPagoSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=(('expensa', 'expensa'), ('multa', 'multa')))
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

        if tipo == 'expensa':
            expensa = ExpensasMensuales.objects.filter(
                id=objetivo_id,
                vivienda__propiedad__persona=persona,
            ).first()
            if not expensa:
                raise serializers.ValidationError('La expensa indicada no existe o no pertenece al usuario.')
            pendiente = max(Decimal('0'), expensa.monto_total - total_pagado_expensa(expensa))
            if pendiente <= 0:
                raise serializers.ValidationError('La expensa seleccionada ya se encuentra pagada.')
            if monto is None:
                monto = pendiente
            if monto <= 0:
                raise serializers.ValidationError('El monto a pagar debe ser mayor a cero.')
            if monto > pendiente:
                raise serializers.ValidationError('El monto supera el saldo pendiente de la expensa.')
            attrs['expensa'] = expensa
            attrs['monto'] = monto
            attrs['pendiente'] = pendiente - monto
        else:
            multa = MultasSanciones.objects.filter(
                id=objetivo_id,
                persona_infractor=persona,
            ).first()
            if not multa:
                multa = MultasSanciones.objects.filter(
                    id=objetivo_id,
                    persona_responsable=persona,
                ).first()
            if not multa:
                raise serializers.ValidationError('La multa indicada no existe o no pertenece al usuario.')
            pendiente = max(Decimal('0'), multa.monto - total_pagado_multa(multa))
            if pendiente <= 0:
                raise serializers.ValidationError('La multa seleccionada ya se encuentra pagada.')
            if monto is None:
                monto = pendiente
            if monto <= 0:
                raise serializers.ValidationError('El monto a pagar debe ser mayor a cero.')
            if monto != pendiente:
                raise serializers.ValidationError('Las multas solo admiten el pago del total adeudado.')
            attrs['multa'] = multa
            attrs['monto'] = monto
            attrs['pendiente'] = Decimal('0')

        attrs['metodo_pago'] = metodo_pago
        return attrs

    def create(self, validated_data):
        persona: Persona = self.context['persona']
        usuario = self.context['request'].user
        expensa: Optional[ExpensasMensuales] = validated_data.get('expensa')
        multa: Optional[MultasSanciones] = validated_data.get('multa')
        monto: Decimal = validated_data['monto']
        metodo_pago: str = validated_data['metodo_pago']
        referencia: str = validated_data.get('referencia') or ''

        referencia_generada = referencia.strip() or timezone.now().strftime('SIM-%Y%m%d%H%M%S')

        with transaction.atomic():
            pago = Pagos.objects.create(
                persona=persona,
                tipo_pago='expensa' if expensa else 'multa',
                expensa=expensa,
                multa=multa,
                monto=monto,
                metodo_pago=metodo_pago,
                numero_comprobante=referencia_generada,
                estado='procesado',
                procesado_por=usuario,
            )

            if expensa:
                total = total_pagado_expensa(expensa)
                expensa.estado = 'pagada' if total >= expensa.monto_total else 'parcial'
                expensa.save(update_fields=['estado'])

            if multa:
                total = total_pagado_multa(multa)
                if total >= multa.monto:
                    multa.estado = 'pagada'
                    multa.fecha_pago = timezone.now()
                    multa.save(update_fields=['estado', 'fecha_pago'])
                else:
                    multa.save(update_fields=['estado'])

        return pago

    def to_representation(self, instance):
        return PagoDetailSerializer(instance).data
