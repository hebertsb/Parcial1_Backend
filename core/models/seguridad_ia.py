# Modelos para Módulo 2 - Seguridad e IA
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from decimal import Decimal


User = get_user_model()

# Tabla de cámaras de seguridad
class CamaraSeguridad(models.Model):
    codigo_camara = models.CharField(max_length=50, unique=True)
    nombre_ubicacion = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)
    puerto = models.IntegerField(default=80)
    tipo_camara = models.CharField(max_length=30, default='ip')
    estado = models.CharField(max_length=30, default='activa', choices=[('activa', 'Activa'), ('inactiva', 'Inactiva'), ('mantenimiento', 'Mantenimiento')])
    ultima_conexion = models.DateTimeField(null=True, blank=True)
    ultima_deteccion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.codigo_camara

# Tabla de lecturas de placas OCR
class LecturaPlacaOCR(models.Model):
    camara = models.ForeignKey(CamaraSeguridad, on_delete=models.CASCADE)
    placa_detectada = models.CharField(max_length=20)
    vehiculo_registrado = models.ForeignKey('core.Vehiculo', null=True, blank=True, on_delete=models.SET_NULL)
    fecha_hora_lectura = models.DateTimeField(auto_now_add=True)
    imagen_placa_url = models.URLField(null=True, blank=True)
    nivel_confianza_ocr = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'))
    estado_verificacion = models.CharField(max_length=30, default='automatica')
    acceso_autorizado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.placa_detectada

# Tabla de accesos vehiculares
class AccesoVehicular(models.Model):
    vehiculo = models.ForeignKey('core.Vehiculo', null=True, blank=True, on_delete=models.SET_NULL)
    placa_detectada = models.CharField(max_length=20)
    tipo_acceso = models.CharField(max_length=50, default='propietario_tag')
    metodo_deteccion = models.CharField(max_length=30, default='tag_rfid')
    fecha_hora_entrada = models.DateTimeField()
    fecha_hora_salida = models.DateTimeField(null=True, blank=True)
    guardia_entrada = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='guardia_entrada', on_delete=models.SET_NULL)
    guardia_salida = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='guardia_salida', on_delete=models.SET_NULL)
    puerta_utilizada = models.CharField(max_length=20, default='propietarios')
    acceso_autorizado = models.BooleanField(default=True)
    observaciones = models.TextField(null=True, blank=True)
    foto_entrada_url = models.URLField(null=True, blank=True)
    foto_salida_url = models.URLField(null=True, blank=True)
    lectura_ocr = models.ForeignKey(LecturaPlacaOCR, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Acceso Vehicular {self.placa_detectada}"

# Tabla de detecciones de IA
class DeteccionIA(models.Model):
    camara = models.ForeignKey(CamaraSeguridad, on_delete=models.CASCADE)
    tipo_deteccion = models.CharField(max_length=100)
    descripcion_automatica = models.TextField()
    ubicacion_deteccion = models.CharField(max_length=100)
    fecha_hora_deteccion = models.DateTimeField(auto_now_add=True)
    imagen_captura_url = models.URLField(null=True, blank=True)
    video_evidencia_url = models.URLField(null=True, blank=True)
    nivel_confianza = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.0000'))
    coordenadas_deteccion = models.JSONField(default=dict)
    metadatos_deteccion = models.JSONField(default=dict)
    estado_verificacion = models.CharField(max_length=30, default='pendiente')
    verificada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    fecha_verificacion = models.DateTimeField(null=True, blank=True)
    requiere_accion_inmediata = models.BooleanField(default=False)
    tipo_anomalia = models.CharField(max_length=50, null=True, blank=True)
    genero_multa = models.BooleanField(default=False)
    proveedor_ia = models.CharField(max_length=50, default='Amazon')

    def __str__(self):
        return f"Detección IA {self.tipo_deteccion} - {self.fecha_hora_deteccion}"

# Tabla de reconocimiento facial
class ReconocimientoFacial(models.Model):
    persona = models.OneToOneField('core.Persona', on_delete=models.CASCADE)
    vector_facial = models.TextField()
    imagen_referencia_url = models.URLField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    proveedor_ia = models.CharField(max_length=50, default='Microsoft')
    confianza_modelo = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0.8500'))
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    numero_entrenamientos = models.IntegerField(default=1)

    def __str__(self):
        return f"Reconocimiento Facial - {self.persona.nombre}"