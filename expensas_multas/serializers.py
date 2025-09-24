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

    def validate(self, data):
        """
        Este método se llama antes de la validación del serializer, 
        podemos usarlo para hacer cálculos o modificaciones de los datos.
        """
        # Calcular el monto_total
        monto_total = data['monto_base_administracion'] + data['monto_mantenimiento'] + data['monto_servicios_comunes'] + data['monto_seguridad']
        data['monto_total'] = monto_total

        # Obtener valores de ingresos y egresos, y asignar 0 si no están presentes
        total_ingresos_expensas = data.get('total_ingresos_expensas', Decimal('0.00'))
        total_ingresos_multas = data.get('total_ingresos_multas', Decimal('0.00'))
        total_ingresos_reservas = data.get('total_ingresos_reservas', Decimal('0.00'))
        total_ingresos_otros = data.get('total_ingresos_otros', Decimal('0.00'))
        
        total_egresos_salarios = data.get('total_egresos_salarios', Decimal('0.00'))
        total_egresos_mantenimiento = data.get('total_egresos_mantenimiento', Decimal('0.00'))
        total_egresos_servicios = data.get('total_egresos_servicios', Decimal('0.00'))
        total_egresos_mejoras = data.get('total_egresos_mejoras', Decimal('0.00'))

        # Calcular saldo_final_periodo
        saldo_final = data['saldo_inicial_periodo'] + total_ingresos_expensas + total_ingresos_multas + total_ingresos_reservas + total_ingresos_otros
        saldo_final -= (total_egresos_salarios + total_egresos_mantenimiento + total_egresos_servicios + total_egresos_mejoras)
        data['saldo_final_periodo'] = saldo_final

        return data
