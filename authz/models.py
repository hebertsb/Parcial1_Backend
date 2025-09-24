from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import secrets
import string
from django.utils import timezone


class Rol(models.Model):
    """Modelo de roles del sistema"""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz_rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Persona(models.Model):
    """Modelo para datos personales centralizados"""
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    TIPO_PERSONA_CHOICES = [
        ('administrador', 'Administrador'),
        ('seguridad', 'Seguridad'),
        ('propietario', 'Propietario'),
        ('inquilino', 'Inquilino'),
        ('cliente', 'Cliente'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    documento_identidad = models.CharField(max_length=20, unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    fecha_nacimiento = models.DateField(blank=True, null=True)
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES, blank=True)
    pais = models.CharField(max_length=50, blank=True)
    tipo_persona = models.CharField(max_length=20, choices=TIPO_PERSONA_CHOICES, default='cliente')
    direccion = models.TextField(blank=True)
    # Campos para reconocimiento facial
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', blank=True, null=True)
    encoding_facial = models.JSONField(blank=True, null=True, help_text="Codificación facial para reconocimiento")
    reconocimiento_facial_activo = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz_persona'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()


class UsuarioManager(BaseUserManager):
    """Manager personalizado para Usuario"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Crear y guardar un Usuario con email y password"""
        if not email:
            raise ValueError('El email es obligatorio')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Crear y guardar un superusuario con email y password"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
            
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        return self.get(email=username)  # username es el email en nuestro caso


class Usuario(AbstractUser):
    """Modelo de usuario personalizado integrado con Persona"""
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
        ('SUSPENDIDO', 'Suspendido'),
        ('BLOQUEADO', 'Bloqueado'),
    ]

    # Quitar campos de AbstractUser que no necesitamos
    username = None
    first_name = None
    last_name = None

    # Campos principales
    email = models.EmailField(unique=True)
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE, related_name='usuario', null=True, blank=True)
    roles = models.ManyToManyField(Rol, blank=True, related_name='usuarios')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')

    objects: UsuarioManager = UsuarioManager()  # type: ignore

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'authz_usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.email} ({self.nombres})"

    # Propiedades para compatibilidad con código existente
    @property
    def nombres(self):
        return self.persona.nombre if self.persona else ''

    @property
    def apellidos(self):
        return self.persona.apellido if self.persona else ''

    @property
    def telefono(self):
        return self.persona.telefono if self.persona else ''

    @property
    def fecha_nacimiento(self):
        return self.persona.fecha_nacimiento if self.persona else None

    @property
    def genero(self):
        return self.persona.genero if self.persona else ''

    @property
    def documento_identidad(self):
        return self.persona.documento_identidad if self.persona else ''

    @property
    def pais(self):
        return self.persona.pais if self.persona else ''

    @property
    def nombre_completo(self):
        return self.persona.nombre_completo if self.persona else self.email


class RelacionesPropietarioInquilino(models.Model):
    """Relaciones entre propietarios e inquilinos de viviendas"""
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='propiedades_como_propietario'
    )
    inquilino = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='propiedades_como_inquilino'
    )
    vivienda = models.ForeignKey(
        'core.Vivienda', 
        on_delete=models.CASCADE, 
        related_name='relaciones_propietario_inquilino'
    )
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    monto_alquiler = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz_relaciones_propietario_inquilino'
        verbose_name = 'Relación Propietario-Inquilino'
        verbose_name_plural = 'Relaciones Propietario-Inquilino'
        # Solo una relación activa por vivienda-propietario-inquilino
        constraints = [
            models.UniqueConstraint(
                fields=['propietario', 'inquilino', 'vivienda'],
                condition=models.Q(activo=True),
                name='unique_active_propietario_inquilino_vivienda'
            )
        ]

    def __str__(self):
        return f"{self.propietario.nombres} -> {self.inquilino.nombres} ({self.vivienda})"


class FamiliarPropietario(models.Model):
    """Modelo para registrar familiares de propietarios"""
    PARENTESCO_CHOICES = [
        ('conyugue', 'Cónyuge'),
        ('hijo', 'Hijo/a'),
        ('padre', 'Padre/Madre'),
        ('hermano', 'Hermano/a'),
        ('abuelo', 'Abuelo/a'),
        ('nieto', 'Nieto/a'),
        ('tio', 'Tío/a'),
        ('sobrino', 'Sobrino/a'),
        ('primo', 'Primo/a'),
        ('cuñado', 'Cuñado/a'),
        ('yerno_nuera', 'Yerno/Nuera'),
        ('suegro', 'Suegro/a'),
        ('otro', 'Otro')
    ]

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='familiares'
    )
    persona = models.OneToOneField(
        Persona, 
        on_delete=models.CASCADE, 
        related_name='familiar_propietario'
    )
    parentesco = models.CharField(max_length=20, choices=PARENTESCO_CHOICES)
    parentesco_descripcion = models.CharField(max_length=100, blank=True, help_text="Descripción específica si es 'otro'")
    autorizado_acceso = models.BooleanField(default=True, help_text="Si puede acceder al condominio sin autorización previa")
    puede_autorizar_visitas = models.BooleanField(default=False, help_text="Si puede autorizar visitas en nombre del propietario")
    observaciones = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz_familiar_propietario'
        verbose_name = 'Familiar de Propietario'
        verbose_name_plural = 'Familiares de Propietarios'
        unique_together = ['propietario', 'persona']

    def __str__(self):
        return f"{self.persona.nombre_completo} ({self.parentesco}) - {self.propietario.nombres}"


class SolicitudRegistroPropietario(models.Model):
    """Modelo para gestionar solicitudes de registro de propietarios"""
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente de Revisión'),
        ('EN_REVISION', 'En Revisión'),
        ('APROBADA', 'Aprobada'),
        ('RECHAZADA', 'Rechazada'),
        ('DOCUMENTOS_FALTANTES', 'Documentos Faltantes'),
        ('REQUIERE_ACLARACION', 'Requiere Aclaración'),
    ]

    # Datos del solicitante
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    documento_identidad = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    
    # Información de la propiedad - solo numero de casa
    numero_casa = models.CharField(max_length=20, help_text="Número de casa o departamento (debe existir en el sistema)")
    
    # Vivienda encontrada tras validación
    vivienda_validada = models.ForeignKey(
        'core.Vivienda', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        help_text="Vivienda encontrada en el sistema"
    )
    
    # Estado de la solicitud
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='PENDIENTE')
    comentarios_admin = models.TextField(blank=True, help_text="Comentarios del administrador")
    observaciones = models.TextField(blank=True, help_text="Observaciones de aprobación")
    motivo_rechazo = models.TextField(blank=True, help_text="Motivo del rechazo")
    fecha_rechazo = models.DateTimeField(blank=True, null=True)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitudes_revisadas'
    )
    fecha_revision = models.DateTimeField(blank=True, null=True)
    
    # Usuario creado tras aprobación
    usuario_creado = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitud_registro'
    )
    
    # Token de seguimiento
    token_seguimiento = models.CharField(max_length=50, unique=True, blank=True, help_text="Token único para seguimiento de la solicitud")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authz_solicitud_registro_propietario'
        verbose_name = 'Solicitud de Registro de Propietario'
        verbose_name_plural = 'Solicitudes de Registro de Propietarios'

    def save(self, *args, **kwargs):
        if not self.token_seguimiento:
            self.token_seguimiento = self._generar_token_seguimiento()
        super().save(*args, **kwargs)

    def _generar_token_seguimiento(self):
        """Genera un token único para seguimiento de la solicitud"""
        import uuid
        return str(uuid.uuid4())[:8].upper()

    def __str__(self):
        bloque_info = f" - {self.vivienda_validada.bloque}" if self.vivienda_validada and self.vivienda_validada.bloque else ""
        return f"Solicitud: {self.nombres} {self.apellidos} - {self.numero_casa}{bloque_info} ({self.estado})"

    def validar_vivienda(self):
        """Valida que la vivienda existe y está disponible para registro"""
        from core.models import Vivienda, Propiedad
        
        try:
            vivienda = Vivienda.objects.get(numero_casa=self.numero_casa)
            
            # Verificar que no haya otro propietario ya registrado para esta vivienda
            propietario_existente = Propiedad.objects.filter(
                vivienda=vivienda,
                tipo_tenencia='propietario',
                activo=True
            ).exists()
            
            if propietario_existente:
                return False, f"La vivienda {self.numero_casa} ya tiene un propietario registrado"
            
            self.vivienda_validada = vivienda
            self.save()
            return True, f"Vivienda {self.numero_casa} validada correctamente"
            
        except Vivienda.DoesNotExist:
            return False, f"No existe la vivienda {self.numero_casa} en el sistema"
        except Exception as e:
            return False, f"Error validando vivienda: {str(e)}"

    def aprobar_solicitud(self, revisado_por_usuario):
        """Aprueba la solicitud y crea el usuario propietario"""
        from django.db import transaction
        
        with transaction.atomic():
            # Validar vivienda antes de aprobar
            es_valida, mensaje = self.validar_vivienda()
            if not es_valida:
                raise ValueError(mensaje)
            
            # Crear o obtener persona usando el modelo de authz (centralizado)
            persona, persona_created = Persona.objects.get_or_create(
                documento_identidad=self.documento_identidad,
                defaults={
                    'nombre': self.nombres,
                    'apellido': self.apellidos,
                    'telefono': self.telefono,
                    'email': self.email,
                    'fecha_nacimiento': self.fecha_nacimiento,
                    'tipo_persona': 'propietario'
                }
            )
            
            # Verificar si ya existe un usuario con este email
            usuario_existente = Usuario.objects.filter(email=self.email).first()
            if usuario_existente:
                # Si la persona ya tiene usuario, verificar si puede ser reutilizada
                if usuario_existente.persona and usuario_existente.persona.documento_identidad == self.documento_identidad:
                    # Es la misma persona, solo asignar rol si no lo tiene
                    rol_propietario, _ = Rol.objects.get_or_create(
                        nombre='Propietario',
                        defaults={'descripcion': 'Propietario de vivienda'}
                    )
                    if not usuario_existente.roles.filter(nombre='Propietario').exists():
                        usuario_existente.roles.add(rol_propietario)
                    
                    # Actualizar solicitud
                    self.estado = 'APROBADA'
                    self.revisado_por = revisado_por_usuario
                    self.fecha_revision = timezone.now()
                    self.usuario_creado = usuario_existente
                    self.save()
                    
                    return usuario_existente
                else:
                    raise ValueError(f"Ya existe un usuario con el email {self.email} pero con diferente cédula")
            
            # Crear usuario nuevo con password temporal (debe cambiarse después)
            usuario = Usuario.objects.create_user(
                email=self.email,
                password='temporal123',  # Password temporal, debe cambiarse después
                persona=persona
            )
            
            # Asignar rol de propietario
            rol_propietario, _ = Rol.objects.get_or_create(
                nombre='Propietario',
                defaults={'descripcion': 'Propietario de vivienda'}
            )
            usuario.roles.add(rol_propietario)
            
            # Crear registro en el modelo Propiedad de core para compatibilidad
            try:
                from core.models import Propiedad
                # Usar la persona ya creada del modelo centralizado de authz
                Propiedad.objects.create(
                    vivienda=self.vivienda_validada,
                    persona=persona,  # Usar la persona del modelo authz centralizado
                    tipo_tenencia='propietario',
                    fecha_inicio_tenencia=timezone.now().date(),
                    porcentaje_propiedad=100.00,
                    activo=True
                )
            except Exception as e:
                # Log pero no fallar si hay problema con compatibilidad
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error creando propiedad para compatibilidad: {e}")
                pass
            
            # Actualizar solicitud
            self.estado = 'APROBADA'
            self.revisado_por = revisado_por_usuario
            self.fecha_revision = timezone.now()
            self.usuario_creado = usuario
            self.save()
            
            return usuario