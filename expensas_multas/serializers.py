from rest_framework import serializers
from core.models import ExpensasMensuales
from decimal import Decimal

class ExpensasMensualesSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ExpensasMensuales
        fields = ['id', 'vivienda', 'periodo_year', 'periodo_month', 
                  'monto_base_administracion', 'monto_mantenimiento', 
                  'monto_servicios_comunes', 'monto_seguridad', 
                  'monto_total', 'total_ingresos_expensas', 'total_ingresos_multas',
                  'total_ingresos_reservas', 'total_ingresos_otros', 
                  'total_egresos_salarios', 'total_egresos_mantenimiento', 
                  'total_egresos_servicios', 'total_egresos_mejoras', 
                  'saldo_inicial_periodo', 'saldo_final_periodo', 'estado']

    def validate(self, attrs):
        """
        Este método se llama antes de la validación del serializer, 
        podemos usarlo para hacer cálculos o modificaciones de los datos.
        """
        # Calcular el monto_total
        monto_total = attrs['monto_base_administracion'] + attrs['monto_mantenimiento'] + attrs['monto_servicios_comunes'] + attrs['monto_seguridad']
        attrs['monto_total'] = monto_total

        # Obtener valores de ingresos y egresos, y asignar 0 si no están presentes
        total_ingresos_expensas = attrs.get('total_ingresos_expensas', Decimal('0.00'))
        total_ingresos_multas = attrs.get('total_ingresos_multas', Decimal('0.00'))
        total_ingresos_reservas = attrs.get('total_ingresos_reservas', Decimal('0.00'))
        total_ingresos_otros = attrs.get('total_ingresos_otros', Decimal('0.00'))
        
        total_egresos_salarios = attrs.get('total_egresos_salarios', Decimal('0.00'))
        total_egresos_mantenimiento = attrs.get('total_egresos_mantenimiento', Decimal('0.00'))
        total_egresos_servicios = attrs.get('total_egresos_servicios', Decimal('0.00'))
        total_egresos_mejoras = attrs.get('total_egresos_mejoras', Decimal('0.00'))

        # Calcular saldo_final_periodo
        saldo_final = attrs['saldo_inicial_periodo'] + total_ingresos_expensas + total_ingresos_multas + total_ingresos_reservas + total_ingresos_otros
        saldo_final -= (total_egresos_salarios + total_egresos_mantenimiento + total_egresos_servicios + total_egresos_mejoras)
        attrs['saldo_final_periodo'] = saldo_final

        return attrs
