from rest_framework import serializers
from core.models.propiedades_residentes import EspacioComun, DisponibilidadEspacioComun

class EspacioComunSerializer(serializers.ModelSerializer):
    class Meta:
        model = EspacioComun
        fields = [
            'id', 'nombre', 'descripcion', 'capacidad_maxima', 'precio_por_hora', 'precio_evento_completo',
            'es_gratuito', 'horario_apertura', 'horario_cierre', 'dias_disponibles', 'requiere_pago', 
            'requiere_deposito_garantia', 'monto_deposito', 'genera_ingresos', 'reserva_maxima_dias_anticipacion',
            'reserva_minima_horas_anticipacion', 'activo', 'imagen_url', 'reglas_uso'
        ]

class DisponibilidadEspacioComunSerializer(serializers.ModelSerializer):
    espacio_comun = serializers.PrimaryKeyRelatedField(queryset=EspacioComun.objects.all())  # Relación con EspacioComun

    class Meta:
        model = DisponibilidadEspacioComun
        fields = [
            'id', 'espacio_comun', 'fecha_inicio', 'fecha_fin', 'capacidad_maxima', 
            'bloqueado_por_mantenimiento', 'motivo_bloqueo', 'es_recurrente', 'dias_recurrentes'
        ]
