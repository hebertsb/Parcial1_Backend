from rest_framework import serializers
from core.models.propiedades_residentes import Mantenimiento, TareaMantenimiento
from django.contrib.auth import get_user_model
from django.utils import timezone

# Serializador para Mantenimiento
class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'
    
    def validate(self, attrs):
        # Validación adicional de que la fecha programada no esté en el pasado
        if attrs.get('fecha_programada') and attrs['fecha_programada'] < timezone.now().date():
            raise serializers.ValidationError("La fecha programada no puede ser en el pasado.")
        return attrs
    
    def create(self, validated_data):
        """Creación del mantenimiento y asignación automática de persona y vivienda."""        
        user = self.context['request'].user  # Usuario logueado
        validated_data['creado_por'] = user  # Asignación de quien crea el mantenimiento
        
        # Solo el administrador puede asignar frecuencia, los propietarios/inquilinos no
        if user.is_staff:  # Si el usuario es administrador, permitir frecuencia
            return super().create(validated_data)
        else:  # Para propietarios/inquilinos, la frecuencia es opcional
            validated_data['frecuencia'] = None
            return super().create(validated_data)

# Serializador para TareaMantenimiento
class TareaMantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareaMantenimiento
        fields = '__all__'

    def validate(self, attrs):
        # Validación de que las fechas no se superpongan
        if attrs.get('fecha_inicio') and attrs.get('fecha_fin'):
            if attrs['fecha_inicio'] > attrs['fecha_fin']:
                raise serializers.ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        return attrs
