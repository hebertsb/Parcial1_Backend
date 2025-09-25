# Modelos para Módulo 1 - Propiedades y Residentes
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from decimal import Decimal
from datetime import time
from datetime import datetime

User = get_user_model()

# Importar modelo Persona centralizado de authz
from authz.models import Persona
# Tabla de viviendas
class Vivienda(models.Model):
    numero_casa = models.CharField(max_length=20, unique=True)
    bloque = models.CharField(max_length=10, null=True, blank=True)
    tipo_vivienda = models.CharField(max_length=50, choices=[('casa', 'Casa'), ('departamento', 'Departamento'), ('local', 'Local')])
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2)
    tarifa_base_expensas = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_cobranza = models.CharField(max_length=30, choices=[('por_casa', 'Por casa'), ('por_metro_cuadrado', 'Por metro cuadrado')])
    estado = models.CharField(max_length=20, default='activa', choices=[('activa', 'Activa'), ('inactiva', 'Inactiva'), ('mantenimiento', 'Mantenimiento')])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_casa} - {self.tipo_vivienda}"

# Tabla de propiedades (relaciona vivienda y persona)
# NOTA: Ahora usa authz.Persona como modelo centralizado
class Propiedad(models.Model):
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tipo_tenencia = models.CharField(max_length=20, choices=[('propietario', 'Propietario'), ('inquilino', 'Inquilino')])
    porcentaje_propiedad = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    fecha_inicio_tenencia = models.DateField()
    fecha_fin_tenencia = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Propiedad {self.vivienda.numero_casa} - {self.persona.nombre}"

# Relación entre propietario e inquilino
# Tabla de mascotas
class Mascota(models.Model):
    propietario = models.ForeignKey(Persona, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=50)
    tipo_animal = models.CharField(max_length=30)
    raza = models.CharField(max_length=50, null=True, blank=True)
    edad = models.IntegerField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    vacunas_vigentes = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Tabla de vehículos
class Vehiculo(models.Model):
    propietario = models.ForeignKey(Persona, on_delete=models.CASCADE)
    placa = models.CharField(max_length=20, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    color = models.CharField(max_length=30)
    tipo_vehiculo = models.CharField(max_length=20, choices=[('auto', 'Auto'), ('moto', 'Moto'), ('bicicleta', 'Bicicleta'), ('camion', 'Camión')])
    tag_numero = models.CharField(max_length=50, unique=True)
    tag_activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.placa

# Tabla de familiares residentes
# Tabla de mantenimientos
class Mantenimiento(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50, choices=[('preventivo', 'Preventivo'), ('correctivo', 'Correctivo')])
    fecha_programada = models.DateField(null=True, blank=True)
    fecha_realizacion = models.DateField(null=True, blank=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    estado = models.CharField(max_length=30, default='pendiente', choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En progreso'), ('completado', 'Completado'), ('cancelado', 'Cancelado')])
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='creador_mantenimiento', null=True, on_delete=models.SET_NULL)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

# Tabla de tareas de mantenimiento
class TareaMantenimiento(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, on_delete=models.CASCADE)
    descripcion = models.TextField()
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=30, default='pendiente', choices=[('pendiente', 'Pendiente'), ('en_progreso', 'En progreso'), ('finalizada', 'Finalizada')])

    def __str__(self):
        return f"Tarea {self.descripcion}"

# Tabla de reservas de espacios
class ReservaEspacio(models.Model):
    ESTADO_CHOICES = [
        ('solicitada', 'Solicitada'),
        ('confirmada', 'Confirmada'),
        ('pagada', 'Pagada'),
        ('en_uso', 'En uso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_show', 'No Show'),
    ]
    
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    espacio_comun = models.ForeignKey('core.EspacioComun', on_delete=models.CASCADE)
    fecha_reserva = models.DateField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    tipo_evento = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=30, choices=ESTADO_CHOICES, default='solicitada')
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    monto_deposito = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    aprobada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    observaciones_cliente = models.TextField(null=True, blank=True)
    observaciones_admin = models.TextField(null=True, blank=True)
    calificacion_post_uso = models.IntegerField(null=True, blank=True, choices=[(1, '1 estrella'), (2, '2 estrellas'), (3, '3 estrellas'), (4, '4 estrellas'), (5, '5 estrellas')])
    comentarios_post_uso = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.espacio_comun.nombre} - {self.fecha_reserva}"


# Tabla de espacios comunes
class EspacioComun(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(null=True, blank=True)
    capacidad_maxima = models.IntegerField(default=10)
    precio_por_hora = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    precio_evento_completo = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    es_gratuito = models.BooleanField(default=False)
    horario_apertura = models.TimeField(default=time(6, 0))
    horario_cierre = models.TimeField(default=time(22, 0))
    dias_disponibles = models.JSONField(default=list)
    requiere_pago = models.BooleanField(default=False)
    requiere_deposito_garantia = models.BooleanField(default=False)
    monto_deposito = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    genera_ingresos = models.BooleanField(default=False)
    reserva_maxima_dias_anticipacion = models.IntegerField(default=30)
    reserva_minima_horas_anticipacion = models.IntegerField(default=24)
    activo = models.BooleanField(default=True)
    imagen_url = models.URLField(null=True, blank=True)
    reglas_uso = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    

#tabla aux de espacio comun
class DisponibilidadEspacioComun(models.Model):
    espacio_comun = models.ForeignKey(EspacioComun, related_name='disponibilidad', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    capacidad_maxima = models.IntegerField(default=10)
    bloqueado_por_mantenimiento = models.BooleanField(default=False)
    motivo_bloqueo = models.CharField(max_length=255, null=True, blank=True)
    es_recurrente = models.BooleanField(default=False)
    dias_recurrentes = models.JSONField(default=list)  # Días de la semana (por ejemplo, ['Lunes', 'Martes'])

    class Meta:
        unique_together = ['espacio_comun', 'fecha_inicio', 'fecha_fin']

    def __str__(self):
        return f"Disponibilidad de {self.espacio_comun.nombre} desde {self.fecha_inicio} hasta {self.fecha_fin}"


# Tabla de notificaciones
class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=[('pago', 'Pago'), ('seguridad', 'Seguridad'), ('mantenimiento', 'Mantenimiento'), ('reserva', 'Reserva'), ('general', 'General')])
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    enviada = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    leida = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    origen_evento = models.CharField(max_length=50, null=True, blank=True)
    origen_id = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Notificación: {self.titulo} - {self.usuario.user.username}"


# Tabla de expensas mensuales
# Tabla de expensas mensuales
class ExpensasMensuales(models.Model):
    vivienda = models.ForeignKey('core.Vivienda', on_delete=models.CASCADE)
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




# Tabla de multas y sanciones
class MultasSanciones(models.Model):
    persona_responsable = models.ForeignKey('authz.Persona', on_delete=models.RESTRICT)
    persona_infractor = models.ForeignKey('authz.Persona', related_name='infractores', on_delete=models.RESTRICT)
    tipo_infraccion = models.ForeignKey('TiposInfracciones', on_delete=models.RESTRICT)
    descripcion_detallada = models.TextField()
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_infraccion = models.DateTimeField(auto_now_add=True)
    ubicacion_infraccion = models.CharField(max_length=100)
    estado = models.CharField(max_length=30, default='pendiente', choices=[('pendiente', 'Pendiente'), ('notificada', 'Notificada'), ('pagada', 'Pagada'), ('anulada', 'Anulada'), ('en_disputa', 'En disputa')])
    evidencia_fotos = models.JSONField(default=list)
    generada_por_ia = models.BooleanField(default=False)
    deteccion_ia = models.ForeignKey('core.DeteccionIA', null=True, on_delete=models.SET_NULL)
    camara_origen = models.ForeignKey('core.CamaraSeguridad', null=True, on_delete=models.SET_NULL)
    nivel_confianza_ia = models.DecimalField(max_digits=5, decimal_places=4)
    verificada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    fecha_notificacion = models.DateTimeField(null=True, blank=True)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    metodo_notificacion = models.JSONField(default=list)
    observaciones = models.TextField(null=True, blank=True)
    requiere_audiencia = models.BooleanField(default=False)

    def __str__(self):
        return f"Multa {self.tipo_infraccion.nombre} - {self.persona_infractor.nombre}"

# Tabla de tipos de infracciones
class TiposInfracciones(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    monto_multa = models.DecimalField(max_digits=10, decimal_places=2)
    genera_restriccion = models.BooleanField(default=False)
    tipo_restriccion = models.CharField(max_length=50, null=True, blank=True)
    detectable_por_ia = models.BooleanField(default=False)
    nivel_confianza_minima = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.8500'))
    requiere_verificacion_humana = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

# Tabla de avisos personalizados
class AvisosPersonalizados(models.Model):
    persona_destinatario = models.ForeignKey('authz.Persona', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo_aviso = models.CharField(max_length=50)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_programada_envio = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    canales_envio = models.JSONField(default=list)
    estado_envio = models.CharField(max_length=30, default='programado', choices=[('programado', 'Programado'), ('enviado', 'Enviado'), ('fallido', 'Fallido')])
    fecha_lectura = models.DateTimeField(null=True, blank=True)
    accion_requerida = models.BooleanField(default=False)
    url_accion = models.URLField(null=True, blank=True)
    generado_automaticamente = models.BooleanField(default=False)

    def __str__(self):
        return f"Aviso a {self.persona_destinatario.nombre} - {self.titulo}"

# Tabla de comunicados de administración
class ComunicadosAdministracion(models.Model):
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    tipo_comunicado = models.CharField(max_length=30, default='general')
    dirigido_a = models.JSONField(default=list)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    canal_publicacion = models.JSONField(default=list)
    publicado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.RESTRICT)
    adjuntos = models.JSONField(default=list)
    requiere_confirmacion_lectura = models.BooleanField(default=False)
    leido_por = models.JSONField(default=list)
    prioridad = models.CharField(max_length=20, default='media', choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta'), ('urgente', 'Urgente')])
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.titulo

# Tabla de visitas
class Visita(models.Model):
    persona_autorizante = models.ForeignKey('authz.Persona', on_delete=models.CASCADE)
    nombre_visitante = models.CharField(max_length=100)
    documento_visitante = models.CharField(max_length=20, null=True, blank=True)
    telefono_visitante = models.CharField(max_length=20, null=True, blank=True)
    motivo_visita = models.TextField(null=True, blank=True)
    fecha_hora_programada = models.DateTimeField(null=True, blank=True)
    fecha_hora_llegada = models.DateTimeField(null=True, blank=True)
    fecha_hora_salida = models.DateTimeField(null=True, blank=True)
    estado = models.CharField(max_length=30, default='programada', choices=[('programada', 'Programada'), ('confirmada_telefono', 'Confirmada por teléfono'), ('en_curso', 'En curso'), ('finalizada', 'Finalizada'), ('cancelada', 'Cancelada'), ('no_autorizada', 'No autorizada')])
    codigo_autorizacion = models.CharField(max_length=10, default='upper(substring(md5(random()::text) from 1 for 6))')
    vehiculo_placa = models.CharField(max_length=20, null=True, blank=True)
    guardia_recepcion = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='visitas_atendidas_core')
    llamada_confirmacion_realizada = models.BooleanField(default=False)
    foto_ingreso_url = models.URLField(null=True, blank=True)
    foto_salida_url = models.URLField(null=True, blank=True)
    registro_automatico_ia = models.BooleanField(default=False)
    observaciones = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Visita {self.nombre_visitante} - {self.estado}"