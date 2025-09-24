from django.db import models
from decimal import Decimal

class ExpensasMensuales(models.Model):
   
    vivienda = models.ForeignKey('core.Vivienda', on_delete=models.CASCADE, related_name='expensas')
    periodo_year = models.IntegerField()
    periodo_month = models.IntegerField()
    monto_base_administracion = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_mantenimiento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_servicios_comunes = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_seguridad = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_ingresos_expensas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ingresos_multas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ingresos_reservas = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_ingresos_otros = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_egresos_salarios = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_egresos_mantenimiento = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_egresos_servicios = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_egresos_mejoras = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    saldo_inicial_periodo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    saldo_final_periodo = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    archivo_reporte_url = models.URLField(null=True, blank=True)
    enviado_personas = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=20, default='pendiente', choices=[('pendiente', 'Pendiente'), ('parcial', 'Parcial'), ('pagada', 'Pagada'), ('vencida', 'Vencida'), ('morosa', 'Morosa')])

    class Meta:
        unique_together = ('vivienda', 'periodo_year', 'periodo_month')

    def __str__(self):
        return f"Expensa {self.vivienda.numero_casa} - {self.periodo_year}/{self.periodo_month}"

    # Método para calcular automáticamente los totales
    def calculate_totals(self):
        self.monto_total = (self.monto_base_administracion + self.monto_mantenimiento +
                            self.monto_servicios_comunes + self.monto_seguridad)
        
        # Asumiendo que los totales de ingresos y egresos son la suma de los campos correspondientes
        self.total_ingresos_expensas = self.total_ingresos_expensas or Decimal('0.00')
        self.total_ingresos_multas = self.total_ingresos_multas or Decimal('0.00')
        self.total_ingresos_reservas = self.total_ingresos_reservas or Decimal('0.00')
        self.total_ingresos_otros = self.total_ingresos_otros or Decimal('0.00')

        self.total_egresos_salarios = self.total_egresos_salarios or Decimal('0.00')
        self.total_egresos_mantenimiento = self.total_egresos_mantenimiento or Decimal('0.00')
        self.total_egresos_servicios = self.total_egresos_servicios or Decimal('0.00')
        self.total_egresos_mejoras = self.total_egresos_mejoras or Decimal('0.00')

        # Calcular saldos
        self.saldo_final_periodo = (self.saldo_inicial_periodo + self.total_ingresos_expensas + 
                                    self.total_ingresos_multas + self.total_ingresos_reservas + 
                                    self.total_ingresos_otros - self.total_egresos_salarios - 
                                    self.total_egresos_mantenimiento - self.total_egresos_servicios - 
                                    self.total_egresos_mejoras)
    
    def save(self, *args, **kwargs):
        # Calcular los totales antes de guardar
        self.calculate_totals()
        super().save(*args, **kwargs)
