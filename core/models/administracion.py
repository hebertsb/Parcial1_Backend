# Modelos para Módulo 3 - Administración
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from decimal import Decimal

User = get_user_model()

# Tabla de bitácora de acciones
class BitacoraAcciones(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    rol = models.ForeignKey('authz.Rol', on_delete=models.RESTRICT)
    descripcion = models.TextField()
    ip_address = models.GenericIPAddressField()
    modulo_afectado = models.CharField(max_length=50)
    accion_tipo = models.CharField(max_length=30, choices=[('CREATE', 'Create'), ('UPDATE', 'Update'), ('DELETE', 'Delete'), ('LOGIN', 'Login'), ('LOGOUT', 'Logout')])
    tabla_afectada = models.CharField(max_length=50)
    registro_id = models.IntegerField()
    datos_antes = models.JSONField(default=dict)
    datos_despues = models.JSONField(default=dict)

    def __str__(self):
        return f"Bitacora {self.descripcion} - {self.usuario.user.username}"

# Tabla de logs del sistema
class LogSistema(models.Model):
    fecha_hora = models.DateTimeField(auto_now_add=True)
    nivel = models.CharField(max_length=20, choices=[('DEBUG', 'Debug'), ('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('CRITICAL', 'Critical')], default='INFO')
    modulo = models.CharField(max_length=50)
    accion = models.CharField(max_length=100)
    usuario_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    mensaje = models.TextField()
    datos_adicionales = models.JSONField(default=dict)
    procesado = models.BooleanField(default=False)
    requiere_atencion = models.BooleanField(default=False)

    def __str__(self):
        return f"Log {self.nivel} - {self.modulo}"

# Tabla de reglamentos del condominio
class ReglamentoCondominio(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    categoria = models.CharField(max_length=50, default='general')
    articulo_numero = models.IntegerField()
    seccion = models.CharField(max_length=100, null=True, blank=True)
    fecha_aprobacion = models.DateField()
    vigente = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

# Tabla de configuraciones del sistema
class ConfiguracionSistema(models.Model):
    clave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    tipo_dato = models.CharField(max_length=20, default='string', choices=[('string', 'String'), ('number', 'Number'), ('boolean', 'Boolean'), ('json', 'JSON')])
    categoria = models.CharField(max_length=50, default='general')
    descripcion = models.TextField(null=True, blank=True)
    editable_por_admin = models.BooleanField(default=True)
    requiere_reinicio_sistema = models.BooleanField(default=False)

    def __str__(self):
        return self.clave

# Tabla de indicadores financieros
class IndicadoresFinancieros(models.Model):
    fecha_calculo = models.DateField(auto_now_add=True)
    morosidad_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    morosidad_monto = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ingresos_mes_actual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ingresos_mes_anterior = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    variacion_ingresos_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    egresos_mes_actual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    egresos_mes_anterior = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    variacion_egresos_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    flujo_caja_mes = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    saldo_total_fondos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    ratio_gastos_ingresos = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Indicador Financiero {self.fecha_calculo}"

# Tabla de métricas de espacios comunes
class MetricasEspaciosComunes(models.Model):
    espacio_comun = models.ForeignKey('core.EspacioComun', on_delete=models.CASCADE)
    fecha_reporte = models.DateField(auto_now_add=True)
    total_reservas = models.IntegerField(default=0)
    total_horas_uso = models.IntegerField(default=0)
    ingresos_generados = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    gastos_mantenimiento = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tasa_ocupacion = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    horario_mayor_demanda = models.CharField(max_length=50, null=True, blank=True)
    personas_usuarios_unicos = models.IntegerField(default=0)
    reservas_canceladas = models.IntegerField(default=0)
    no_shows = models.IntegerField(default=0)
    calificacion_promedio = models.DecimalField(max_digits=3, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('espacio_comun', 'fecha_reporte')

    def __str__(self):
        return f"Métricas {self.espacio_comun.nombre} - {self.fecha_reporte}"

# Tabla de métricas de seguridad con IA
class MetricasSeguridadIA(models.Model):
    fecha_reporte = models.DateField(auto_now_add=True, unique=True)
    total_accesos_no_autorizados = models.IntegerField(default=0)
    total_incidentes_detectados = models.IntegerField(default=0)
    total_falsas_alarmas = models.IntegerField(default=0)
    precision_reconocimiento_facial = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    precision_ocr_placas = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    tiempo_respuesta_promedio_alertas = models.IntegerField(default=0)
    camaras_operativas = models.IntegerField(default=0)
    camaras_total = models.IntegerField(default=0)
    detecciones_vehiculos_mes = models.IntegerField(default=0)
    detecciones_personas_mes = models.IntegerField(default=0)
    detecciones_anomalias_mes = models.IntegerField(default=0)
    multas_generadas_automaticamente = models.IntegerField(default=0)

    def __str__(self):
        return f"Métricas de Seguridad IA {self.fecha_reporte}"

# Tabla de movimientos financieros
class MovimientosFinancieros(models.Model):
    fondo = models.ForeignKey('core.FondoCondominio', on_delete=models.RESTRICT)
    tipo_movimiento = models.CharField(max_length=30, choices=[('ingreso', 'Ingreso'), ('egreso', 'Egreso'), ('transferencia_interna', 'Transferencia Interna'), ('ajuste', 'Ajuste')])
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_movimiento = models.DateField()
    categoria = models.CharField(max_length=50)
    proveedor_beneficiario = models.CharField(max_length=100, null=True, blank=True)
    autorizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    estado = models.CharField(max_length=30, default='ejecutado', choices=[('pendiente', 'Pendiente'), ('ejecutado', 'Ejecutado'), ('anulado', 'Anulado')])
    comprobante_numero = models.CharField(max_length=100, null=True, blank=True)
    comprobante_archivo = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"Movimiento {self.concepto} - {self.monto}"

# Tabla de fondos del condominio
class FondoCondominio(models.Model):
    nombre_fondo = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    saldo_minimo_requerido = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    porcentaje_asignacion_expensas = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    requiere_aprobacion_gastos = models.BooleanField(default=False)
    limite_gasto_sin_aprobacion = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.nombre_fondo

# Tabla de pagos
class Pagos(models.Model):
    persona = models.ForeignKey('authz.Persona', on_delete=models.RESTRICT)
    tipo_pago = models.CharField(max_length=30, choices=[('expensa', 'Expensa'), ('multa', 'Multa'), ('reserva', 'Reserva'), ('servicios_adicionales', 'Servicios Adicionales')])
    expensa = models.ForeignKey('core.ExpensasMensuales', null=True, blank=True, on_delete=models.CASCADE)
    multa = models.ForeignKey('core.MultasSanciones', null=True, blank=True, on_delete=models.CASCADE)
    reserva = models.ForeignKey('core.ReservaEspacio', null=True, blank=True, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=30)
    numero_comprobante = models.CharField(max_length=100, null=True, blank=True)
    comprobante_archivo = models.URLField(null=True, blank=True)
    estado = models.CharField(max_length=30, default='procesado', choices=[('procesado', 'Procesado'), ('rechazado', 'Rechazado'), ('pendiente_verificacion', 'Pendiente Verificación'), ('reembolsado', 'Reembolsado')])
    procesado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='pagos_procesados_core')

    def __str__(self):
        return f"Pago {self.tipo_pago} - {self.monto}"

# Tabla de reportes mensuales
class ReporteMensual(models.Model):
    periodo_year = models.IntegerField()
    periodo_month = models.IntegerField()
    titulo = models.CharField(max_length=200)
    url_reporte = models.URLField()
    generado_por_usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('periodo_year', 'periodo_month')

    def __str__(self):
        return f"Reporte {self.titulo} - {self.periodo_year}/{self.periodo_month}"
