from django.db import models
from django.conf import settings
from django.utils import timezone


class Copropietarios(models.Model):
    """Copropietarios de la propiedad"""
    TIPO_RESIDENTE_CHOICES = [
        ('Propietario', 'Propietario'),
        ('Inquilino', 'Inquilino'),
        ('Familiar', 'Familiar'),
        ('Visitante', 'Visitante Frecuente'),
    ]
    
    id = models.AutoField(primary_key=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero_documento = models.CharField(max_length=20, unique=True)
    tipo_documento = models.CharField(max_length=20, choices=[
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ], default='CC')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    unidad_residencial = models.CharField(max_length=50)  # Ej: Apto 101, Casa 23
    tipo_residente = models.CharField(max_length=20, choices=TIPO_RESIDENTE_CHOICES, default='Propietario')
    
    # Relación opcional con el sistema de usuarios authz
    usuario_sistema = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='copropietario_perfil',
        help_text='Usuario del sistema asociado a este copropietario'
    )
    
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'copropietarios'
        verbose_name = 'Copropietario'
        verbose_name_plural = 'Copropietarios'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} - {self.unidad_residencial} ({self.tipo_residente})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class ReconocimientoFacial(models.Model):
    """Datos de reconocimiento facial de copropietarios"""
    PROVEEDOR_CHOICES = [
        ('Microsoft', 'Microsoft Azure Face API'),
        ('Local', 'Reconocimiento Local'),
    ]
    
    id = models.AutoField(primary_key=True)
    copropietario = models.OneToOneField(
        Copropietarios, 
        on_delete=models.CASCADE, 
        related_name='reconocimiento_facial'
    )
    proveedor_ia = models.CharField(max_length=20, choices=PROVEEDOR_CHOICES)
    vector_facial = models.TextField()  # Almacena faceId (Azure) o vector base64 (Local)
    imagen_referencia_url = models.URLField(blank=True, null=True)  # Para Azure
    imagen_referencia_path = models.CharField(max_length=500, blank=True, null=True)  # Para Local
    activo = models.BooleanField(default=True)
    fecha_enrolamiento = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Metadatos adicionales
    confianza_enrolamiento = models.FloatField(blank=True, null=True)
    intentos_verificacion = models.PositiveIntegerField(default=0)
    ultima_verificacion = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'reconocimiento_facial'
        verbose_name = 'Reconocimiento Facial'
        verbose_name_plural = 'Reconocimientos Faciales'

    def __str__(self):
        return f"Reconocimiento {self.proveedor_ia} - {self.copropietario.nombre_completo}"


class BitacoraAcciones(models.Model):
    """Bitácora de acciones del sistema"""
    TIPO_ACCION_CHOICES = [
        ('LOGIN', 'Inicio de Sesión'),
        ('LOGOUT', 'Cierre de Sesión'),
        ('ENROLL_FACE', 'Enrolamiento Biométrico'),
        ('VERIFY_FACE', 'Verificación Biométrica'),
        ('DELETE_FACE', 'Eliminación Biométrico'),
        ('ACCESS_GRANTED', 'Acceso Concedido'),
        ('ACCESS_DENIED', 'Acceso Denegado'),
        ('SYSTEM_ERROR', 'Error del Sistema'),
    ]
    
    id = models.AutoField(primary_key=True)
    # Cambiar para usar el nuevo modelo de usuario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acciones_bitacora'
    )
    copropietario = models.ForeignKey(
        Copropietarios, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acciones_bitacora'
    )
    tipo_accion = models.CharField(max_length=20, choices=TIPO_ACCION_CHOICES)
    descripcion = models.TextField()
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # Metadatos específicos para reconocimiento facial
    proveedor_ia = models.CharField(max_length=20, blank=True, null=True)
    confianza = models.FloatField(blank=True, null=True)
    resultado_match = models.BooleanField(blank=True, null=True)
    
    fecha_accion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bitacora_acciones'
        verbose_name = 'Bitácora de Acción'
        verbose_name_plural = 'Bitácora de Acciones'
        ordering = ['-fecha_accion']

    def __str__(self):
        usuario_str = f"Usuario: {self.usuario.email}" if self.usuario else "Usuario: Sistema"
        coprop_str = f"Copropietario: {self.copropietario.nombre_completo}" if self.copropietario else ""
        return f"{self.tipo_accion} - {usuario_str} {coprop_str} - {self.fecha_accion}"


# Función auxiliar para logging en bitácora
def fn_bitacora_log(tipo_accion, descripcion, usuario=None, copropietario=None, 
                   direccion_ip=None, user_agent=None, proveedor_ia=None, 
                   confianza=None, resultado_match=None):
    """
    Función auxiliar para crear registros en bitácora de acciones
    """
    BitacoraAcciones.objects.create(
        usuario=usuario,
        copropietario=copropietario,
        tipo_accion=tipo_accion,
        descripcion=descripcion,
        direccion_ip=direccion_ip,
        user_agent=user_agent,
        proveedor_ia=proveedor_ia,
        confianza=confianza,
        resultado_match=resultado_match
    )
