from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
import secrets
import string

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    permisos_json = models.JSONField(default=dict)
    puede_autorizar_visitas = models.BooleanField(default=False)
    puede_generar_multas = models.BooleanField(default=False)
    acceso_web = models.BooleanField(default=True)
    acceso_movil = models.BooleanField(default=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nombre

class Persona(models.Model):
    """Modelo centralizado para información personal"""
    TIPO_PERSONA_CHOICES = [
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('familiar', 'Familiar'),
        ('personal_servicio', 'Personal de servicio'),
        ('administrador', 'Administrador'),
        ('seguridad', 'Seguridad')
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('CI', 'Cédula de Identidad'),
        ('PASAPORTE', 'Pasaporte'),
        ('RUN', 'RUN'),
        ('DNI', 'DNI')
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento_identidad = models.CharField(max_length=20, unique=True)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='CI')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=[('M','Masculino'),('F','Femenino')], blank=True, null=True)
    estado_civil = models.CharField(max_length=20, blank=True, null=True)
    profesion = models.CharField(max_length=100, blank=True, null=True)
    tipo_persona = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES)
    pais = models.CharField(max_length=50, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class UsuarioManager(BaseUserManager):
    def create_user(self, email, persona, password=None, **extra_fields):
        """
        Crear usuario con objeto Persona asociado
        """
        if not email:
            raise ValueError('El campo email es obligatorio')
        if not persona:
            raise ValueError('El objeto persona es obligatorio')
        if not isinstance(persona, Persona):
            raise ValueError('El parámetro persona debe ser una instancia del modelo Persona')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            persona=persona,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, persona, password=None, **extra_fields):
        """
        Crear superusuario con objeto Persona asociado
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('estado', 'ACTIVO')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
            
        return self.create_user(email, persona, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo de usuario personalizado integrado con Persona"""
    ESTADOS = [
        ("ACTIVO", "ACTIVO"),
        ("INACTIVO", "INACTIVO"),
        ("BLOQUEADO", "BLOQUEADO")
    ]
    
    # Relación con Persona (reemplaza campos personales)
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE,
        related_name='usuario_cuenta',
        help_text='Información personal del usuario'
    )
    
    # Campos específicos del sistema de usuarios
    email = models.EmailField(max_length=254, unique=True)
    roles = models.ManyToManyField(Rol, related_name="usuarios", blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="ACTIVO")
    
    # Campos de control
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    # Campos adicionales del sistema
    ultimo_acceso = models.DateTimeField(blank=True, null=True)
    token_dispositivo_movil = models.CharField(max_length=100, blank=True, null=True)
    comandos_voz_activos = models.BooleanField(default=False)
    reconocimiento_facial_activo = models.BooleanField(default=False)

    # Evitar conflictos con el modelo User de Django
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='authz_usuarios',
        help_text='Los grupos a los que pertenece este usuario.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='authz_usuarios',
        help_text='Permisos específicos para este usuario.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # persona se manejará en el manager

    objects = UsuarioManager()

    def __str__(self):
        if self.persona:
            return f"{self.persona.nombre_completo} <{self.email}>"
        return f"Usuario <{self.email}>"

    @property
    def nombres(self):
        """Compatibilidad hacia atrás"""
        return self.persona.nombre if self.persona else ""
    
    @property
    def apellidos(self):
        """Compatibilidad hacia atrás"""
        return self.persona.apellido if self.persona else ""

# Modelos adicionales para el sistema de condominio

class Vivienda(models.Model):
    """Modelo de viviendas del condominio"""
    TIPO_VIVIENDA_CHOICES = [
        ('casa', 'Casa'),
        ('departamento', 'Departamento'),
        ('local', 'Local')
    ]
    
    TIPO_COBRANZA_CHOICES = [
        ('por_casa', 'Por casa'),
        ('por_metro_cuadrado', 'Por metro cuadrado')
    ]
    
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('inactiva', 'Inactiva'),
        ('mantenimiento', 'Mantenimiento')
    ]
    
    numero_casa = models.CharField(max_length=20, unique=True)
    bloque = models.CharField(max_length=10, blank=True, null=True)
    tipo_vivienda = models.CharField(max_length=50, choices=TIPO_VIVIENDA_CHOICES)
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2)
    tarifa_base_expensas = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_cobranza = models.CharField(max_length=30, choices=TIPO_COBRANZA_CHOICES)
    estado = models.CharField(max_length=20, default='activa', choices=ESTADO_CHOICES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.numero_casa} - {self.tipo_vivienda}"

class Propiedad(models.Model):
    """Relación entre vivienda y persona"""
    TIPO_TENENCIA_CHOICES = [
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino')
    ]
    
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
    tipo_tenencia = models.CharField(max_length=20, choices=TIPO_TENENCIA_CHOICES)
    porcentaje_propiedad = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    fecha_inicio_tenencia = models.DateField()
    fecha_fin_tenencia = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Propiedad {self.vivienda.numero_casa} - {self.persona.nombre_completo}"

class RelacionesPropietarioInquilino(models.Model):
    """Relación entre propietario e inquilino con constraint único para activos"""
    propietario = models.ForeignKey(
        Persona, 
        related_name='relaciones_como_propietario', 
        on_delete=models.RESTRICT
    )
    inquilino = models.ForeignKey(
        Persona, 
        related_name='relaciones_como_inquilino', 
        on_delete=models.CASCADE
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    contrato_alquiler = models.TextField()
    monto_alquiler = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        # Constraint único para relaciones activas solamente
        constraints = [
            models.UniqueConstraint(
                fields=['propietario', 'inquilino'],
                condition=models.Q(activo=True),
                name='unique_active_propietario_inquilino'
            )
        ]

    def __str__(self):
        return f"{self.propietario.nombre_completo} - {self.inquilino.nombre_completo}"

class Visita(models.Model):
    """Modelo de visitas con código de autorización seguro"""
    ESTADO_CHOICES = [
        ('programada', 'Programada'),
        ('confirmada_telefono', 'Confirmada por teléfono'),
        ('en_curso', 'En curso'),
        ('finalizada', 'Finalizada'),
        ('cancelada', 'Cancelada'),
        ('no_autorizada', 'No autorizada')
    ]
    
    persona_autorizante = models.ForeignKey(Persona, on_delete=models.CASCADE)
    nombre_visitante = models.CharField(max_length=100)
    documento_visitante = models.CharField(max_length=20, blank=True, null=True)
    telefono_visitante = models.CharField(max_length=20, blank=True, null=True)
    motivo_visita = models.TextField(blank=True, null=True)
    fecha_hora_programada = models.DateTimeField(blank=True, null=True)
    fecha_hora_llegada = models.DateTimeField(blank=True, null=True)
    fecha_hora_salida = models.DateTimeField(blank=True, null=True)
    estado = models.CharField(max_length=30, default='programada', choices=ESTADO_CHOICES)
    codigo_autorizacion = models.CharField(max_length=10, blank=True, unique=True)
    vehiculo_placa = models.CharField(max_length=20, blank=True, null=True)
    guardia_recepcion = models.ForeignKey(
        Usuario, 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL
    )
    llamada_confirmacion_realizada = models.BooleanField(default=False)
    foto_ingreso_url = models.URLField(blank=True, null=True)
    foto_salida_url = models.URLField(blank=True, null=True)
    registro_automatico_ia = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        """Generar código de autorización seguro al guardar"""
        if not self.codigo_autorizacion:
            self.codigo_autorizacion = self.generar_codigo_autorizacion()
        super().save(*args, **kwargs)

    def generar_codigo_autorizacion(self):
        """Generar código alfanumérico seguro de 6 caracteres"""
        while True:
            codigo = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if not Visita.objects.filter(codigo_autorizacion=codigo).exists():
                return codigo

    def __str__(self):
        return f"Visita {self.nombre_visitante} - {self.estado}"

class Pagos(models.Model):
    """Modelo polimórfico de pagos usando GenericForeignKey"""
    TIPO_PAGO_CHOICES = [
        ('expensa', 'Expensa'),
        ('multa', 'Multa'),
        ('reserva', 'Reserva'),
        ('servicios_adicionales', 'Servicios Adicionales')
    ]
    
    ESTADO_CHOICES = [
        ('procesado', 'Procesado'),
        ('rechazado', 'Rechazado'),
        ('pendiente_verificacion', 'Pendiente Verificación'),
        ('reembolsado', 'Reembolsado')
    ]
    
    persona = models.ForeignKey(Persona, on_delete=models.RESTRICT)
    tipo_pago = models.CharField(max_length=30, choices=TIPO_PAGO_CHOICES)
    
    # Relación genérica para objetos pagables
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    objeto_pagable = GenericForeignKey('content_type', 'object_id')
    
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=30)
    numero_comprobante = models.CharField(max_length=100, blank=True, null=True)
    comprobante_archivo = models.URLField(blank=True, null=True)
    estado = models.CharField(max_length=30, default='procesado', choices=ESTADO_CHOICES)
    procesado_por = models.ForeignKey(
        Usuario, 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Pago {self.tipo_pago} - {self.monto} - {self.persona.nombre_completo}"

    class Meta:
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['tipo_pago', 'estado']),
        ]
