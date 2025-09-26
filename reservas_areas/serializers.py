from rest_framework import serializers
from core.models.propiedades_residentes import ReservaEspacio
from authz.models import Persona
from core.models.propiedades_residentes import EspacioComun
from datetime import datetime

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
        if value < datetime.today().date():  # Aquí cambiamos la forma de obtener la fecha
            raise serializers.ValidationError("La fecha de reserva no puede ser en el pasado.")
        return value
