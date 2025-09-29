from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Iterable, Optional, Tuple

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from core.models.administracion import Pagos
from core.models.propiedades_residentes import (
    ExpensasMensuales,
    MultasSanciones,
    Persona,
    Propiedad,
    TiposInfracciones,
    Vivienda,
)
from seguridad.models import Copropietarios

# Estados de pagos que cuentan como dinero efectivamente recibido
CONFIRMED_PAYMENT_STATES = ('procesado', 'pendiente_verificacion')


def get_persona_for_user(user) -> Optional[Persona]:
    """Obtiene la persona vinculada al usuario autenticado."""
    if not getattr(user, 'is_authenticated', False):
        return None

    persona = Persona.objects.filter(email__iexact=user.email).first()
    if persona:
        return persona

    if getattr(user, 'documento_identidad', None):
        persona = Persona.objects.filter(documento_identidad=user.documento_identidad).first()
        if persona:
            return persona

    copropietario = Copropietarios.objects.filter(usuario_sistema=user).first()
    if copropietario:
        persona = Persona.objects.filter(documento_identidad=copropietario.numero_documento).first()
        if persona:
            return persona
        persona = Persona.objects.filter(email__iexact=copropietario.email).first()
        if persona:
            return persona

    return None


def ensure_persona_for_user(user) -> Persona:
    persona = get_persona_for_user(user)
    if persona:
        return persona

    nombres = getattr(user, 'nombres', 'Usuario')
    apellidos = getattr(user, 'apellidos', 'Demo')
    email = getattr(user, 'email', None)
    documento = getattr(user, 'documento_identidad', None) or f'USR-{getattr(user, "id", 0)}'
    telefono = getattr(user, 'telefono', '')
    fecha_nacimiento = getattr(user, 'fecha_nacimiento', None) or date(1990, 1, 1)

    persona = Persona.objects.create(
        nombre=nombres,
        apellido=apellidos,
        email=email or f'{documento}@example.com',
        documento_identidad=documento,
        tipo_documento='CI',
        telefono=telefono or None,
        fecha_nacimiento=fecha_nacimiento,
        estado_civil='Soltero',
        profesion='Propietario',
        tipo_persona='propietario',
    )
    return persona


def ensure_vivienda_y_propiedad(persona: Persona) -> Tuple[Vivienda, Propiedad]:
    propiedad = Propiedad.objects.filter(persona=persona, activo=True).select_related('vivienda').first()
    if propiedad:
        return propiedad.vivienda, propiedad

    numero_casa = f'A-{persona.id:03d}'
    vivienda = Vivienda.objects.create(
        numero_casa=numero_casa,
        bloque='A',
        tipo_vivienda='departamento',
        metros_cuadrados=Decimal('95.00'),
        tarifa_base_expensas=Decimal('300.00'),
        tipo_cobranza='por_casa',
        estado='activa',
    )

    propiedad = Propiedad.objects.create(
        vivienda=vivienda,
        persona=persona,
        tipo_tenencia='propietario',
        fecha_inicio_tenencia=timezone.now().date(),
        porcentaje_propiedad=Decimal('100.00'),
        activo=True,
    )
    return vivienda, propiedad


def crear_expensa_demo(persona: Persona, monto_total: Decimal = Decimal('450.00')) -> ExpensasMensuales:
    vivienda, _ = ensure_vivienda_y_propiedad(persona)
    last = ExpensasMensuales.objects.filter(vivienda=vivienda).order_by('-periodo_year', '-periodo_month').first()
    if last:
        year = last.periodo_year
        month = last.periodo_month + 1
        if month > 12:
            month = 1
            year += 1
    else:
        now = timezone.now()
        year = now.year
        month = now.month

    defaults = {
        'monto_base_administracion': Decimal('250.00'),
        'monto_mantenimiento': Decimal('80.00'),
        'monto_servicios_comunes': Decimal('70.00'),
        'monto_seguridad': Decimal('50.00'),
        'monto_total': monto_total,
        'total_ingresos_expensas': Decimal('0.00'),
        'total_ingresos_multas': Decimal('0.00'),
        'total_ingresos_reservas': Decimal('0.00'),
        'total_ingresos_otros': Decimal('0.00'),
        'total_egresos_salarios': Decimal('0.00'),
        'total_egresos_mantenimiento': Decimal('0.00'),
        'total_egresos_servicios': Decimal('0.00'),
        'total_egresos_mejoras': Decimal('0.00'),
        'saldo_inicial_periodo': Decimal('0.00'),
        'saldo_final_periodo': Decimal('0.00'),
        'estado': 'pendiente',
    }

    expensa, created = ExpensasMensuales.objects.get_or_create(
        vivienda=vivienda,
        periodo_year=year,
        periodo_month=month,
        defaults=defaults,
    )
    if not created and expensa.estado == 'pagada':
        expensa.estado = 'pendiente'
        expensa.save(update_fields=['estado'])
    return expensa


def crear_multa_demo(persona: Persona, monto: Decimal = Decimal('150.00')) -> MultasSanciones:
    tipo, _ = TiposInfracciones.objects.get_or_create(
        codigo='DEMO-001',
        defaults={
            'nombre': 'Ruido Excesivo',
            'descripcion': 'Incumplimiento del reglamento por ruido en horario restringido.',
            'monto_multa': monto,
            'genera_restriccion': False,
            'detectable_por_ia': False,
            'nivel_confianza_minima': Decimal('0.8500'),
        },
    )
    multa = MultasSanciones.objects.create(
        persona_responsable=persona,
        persona_infractor=persona,
        tipo_infraccion=tipo,
        descripcion_detallada='Reporte de ruido excesivo generado automaticamente para pruebas.',
        monto=monto,
        ubicacion_infraccion='Area comun',
        evidencia_fotos=[],
        generada_por_ia=False,
        deteccion_ia=None,
        camara_origen=None,
        nivel_confianza_ia=Decimal('0.9500'),
        verificada_por=None,
        metodo_notificacion=[],
        observaciones='Caso demo',
        requiere_audiencia=False,
    )
    return multa


def _sum_pagos_queryset(qs) -> Decimal:
    total = qs.exclude(estado__in=('rechazado', 'reembolsado')).aggregate(total=Sum('monto'))['total']
    return total or Decimal('0')


def total_pagado_expensa(expensa: ExpensasMensuales) -> Decimal:
    pagos = Pagos.objects.filter(expensa=expensa, estado__in=CONFIRMED_PAYMENT_STATES)
    return _sum_pagos_queryset(pagos)


def total_pagado_multa(multa: MultasSanciones) -> Decimal:
    pagos = Pagos.objects.filter(multa=multa, estado__in=CONFIRMED_PAYMENT_STATES)
    return _sum_pagos_queryset(pagos)


def viviendas_de_persona(persona: Persona) -> Iterable[int]:
    return Propiedad.objects.filter(persona=persona, activo=True).values_list('vivienda_id', flat=True)


def expensas_pendientes(persona: Persona):
    estados_pendientes = ('pendiente', 'morosa', 'vencida', 'parcial')
    viviendas_ids = list(viviendas_de_persona(persona))
    if not viviendas_ids:
        return ExpensasMensuales.objects.none()
    return ExpensasMensuales.objects.filter(
        vivienda_id__in=viviendas_ids,
        estado__in=estados_pendientes,
    ).order_by('-periodo_year', '-periodo_month')


def multas_pendientes(persona: Persona):
    estados_pendientes = ('pendiente', 'notificada', 'en_disputa')
    return MultasSanciones.objects.filter(
        Q(persona_responsable=persona) | Q(persona_infractor=persona),
        estado__in=estados_pendientes,
    ).order_by('-fecha_infraccion')

def total_pagado_reserva(reserva):
    """
    Calcula el total pagado por una reserva. 
    Suma los montos de los pagos procesados que estén asociados a la reserva.
    """
    # Filtrar los pagos procesados asociados a la reserva
    pagos_reserva = Pagos.objects.filter(reserva=reserva, estado='procesado')
    
    # Sumar los montos de todos los pagos asociados
    total_pagado = sum(pago.monto for pago in pagos_reserva)
    
    return total_pagado