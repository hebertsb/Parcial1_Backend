from rest_framework import serializers
from core.models.propiedades_residentes import ExpensasMensuales

class ExpensasMensualesSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpensasMensuales
        fields = [
            'id', 'vivienda', 'periodo_year', 'periodo_month',
            'monto_base_administracion', 'monto_mantenimiento',
            'monto_servicios_comunes', 'monto_seguridad',
            'monto_total', 'total_ingresos_expensas', 'total_ingresos_multas',
            'total_ingresos_reservas', 'total_ingresos_otros',
            'total_egresos_salarios', 'total_egresos_mantenimiento',
            'total_egresos_servicios', 'total_egresos_mejoras',
            'saldo_inicial_periodo', 'saldo_final_periodo', 'estado'
        ]

    def validate(self, attrs):
        # Asegurar que la vivienda existe y está activa
        vivienda = attrs.get('vivienda')
        if vivienda and not vivienda.activo:
            raise serializers.ValidationError("La propiedad asociada no está activa.")

        # Valores seguros por defecto
        for field in [
            'total_ingresos_expensas', 'total_ingresos_multas',
            'total_ingresos_reservas', 'total_ingresos_otros',
            'total_egresos_salarios', 'total_egresos_mantenimiento',
            'total_egresos_servicios', 'total_egresos_mejoras',
        ]:
            if attrs.get(field) is None:
                attrs[field] = 0.0

        if attrs.get('saldo_inicial_periodo') is None:
            attrs['saldo_inicial_periodo'] = 0.0

        return attrs

    def create(self, validated_data):
        """
        Aprovecha calculate_totals() del modelo.
        """
        expensa = ExpensasMensuales(**validated_data)
        expensa.calculate_totals()
        expensa.save()
        return expensa

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.calculate_totals()
        instance.save()
        return instance
