from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import secrets
import string
from django.utils import timezone
        # Mover imágenes de reconocimiento facial a la carpeta definitiva del propietario en Dropbox


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
    @property
    def foto_perfil_url(self):
        """Devuelve la URL pública de Dropbox para foto_perfil si existe."""
        return self.foto_perfil if self.foto_perfil else None
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
    foto_perfil = models.CharField(max_length=512, blank=True, null=True, help_text="URL pública de la foto de perfil (Dropbox)")
    encoding_facial = models.JSONField(blank=True, null=True, help_text="Lista de codificaciones faciales para reconocimiento (puede ser una lista de listas)")
    def agregar_encoding_facial(self, nuevo_encoding):
        """Agrega un nuevo encoding facial a la lista de encodings."""
        if not self.encoding_facial:
            self.encoding_facial = []
        # Si solo hay un encoding antiguo (no lista de listas), conviértelo
        if self.encoding_facial and isinstance(self.encoding_facial[0], (float, int)):
            self.encoding_facial = [self.encoding_facial]
        self.encoding_facial.append(list(nuevo_encoding))
        self.save()
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
    @property
    def foto_perfil_url(self):
        """Devuelve la URL pública de Dropbox para foto_perfil si existe."""
        if self.foto_perfil:
            try:
                from core.utils.dropbox_upload import DROPBOX_TOKEN
                import dropbox
                dbx = dropbox.Dropbox(DROPBOX_TOKEN)
                destino = self.foto_perfil.name if hasattr(self.foto_perfil, 'name') else str(self.foto_perfil)
                shared_link_metadata = dbx.sharing_create_shared_link_with_settings(destino)
                url = shared_link_metadata.url.replace('?dl=0', '?dl=1')
                return url
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Error obteniendo URL pública de Dropbox para foto_perfil: {e}")
                return None
        return None
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
    fecha_aprobacion = models.DateTimeField(blank=True, null=True, help_text="Fecha de aprobación de la solicitud")
    
    # Usuario creado tras aprobación
    usuario_creado = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='solicitud_registro'
    )
    
    # Imagen del solicitante
    foto_perfil = models.ImageField(upload_to='solicitudes_fotos/', blank=True, null=True, help_text="Foto del solicitante para reconocimiento/acceso")

    # URLs de fotos de reconocimiento facial subidas a Dropbox
    fotos_reconocimiento_urls = models.JSONField(default=list, blank=True, help_text="Lista de URLs de fotos para reconocimiento facial (Dropbox)")

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
        import logging
        logger = logging.getLogger(__name__)
        # Mover imágenes de reconocimiento facial a la carpeta definitiva del propietario en Dropbox
        # Crear o obtener persona antes del bloque try
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
        try:
            from core.utils.dropbox_upload import DROPBOX_TOKEN
            import dropbox
            dbx = dropbox.Dropbox(DROPBOX_TOKEN)
            documento_identidad = self.documento_identidad
            nueva_carpeta = f"/Aplicaciones/FotoVisita/Propietarios/{documento_identidad}"
            nuevas_fotos_urls = []
            url_foto_perfil = None
            for idx, foto in enumerate(self.fotos_reconocimiento_urls):
                foto_path = foto['path'] if isinstance(foto, dict) and 'path' in foto else foto
                nombre_archivo = foto_path.split('/')[-1]
                origen = foto_path
                destino = f"{nueva_carpeta}/{nombre_archivo}"
                try:
                    # Solo mover si origen y destino son diferentes
                    if origen != destino:
                        dbx.files_move_v2(origen, destino, allow_shared_folder=True, autorename=True)
                    shared_link_metadata = dbx.sharing_create_shared_link_with_settings(destino)
                    url = shared_link_metadata.url.replace('?dl=0', '?dl=1')
                    nuevas_fotos_urls.append({'path': destino, 'url': url})
                    # Guardar la primera imagen como foto_perfil en Persona
                    if idx == 0:
                        url_foto_perfil = url
                except Exception as e:
                    logger.warning(f"Error moviendo/compartiendo imagen en Dropbox: {e}")
                    # Intentar solo generar el enlace si el movimiento falla
                    try:
                        shared_link_metadata = dbx.sharing_create_shared_link_with_settings(destino)
                        url = shared_link_metadata.url.replace('?dl=0', '?dl=1')
                        nuevas_fotos_urls.append({'path': destino, 'url': url})
                        if idx == 0:
                            url_foto_perfil = url
                    except Exception as e2:
                        logger.warning(f"Error generando enlace público en Dropbox: {e2}")
                        # Si el error es 'shared_link_already_exists', intentar recuperar el enlace existente
                        try:
                            links = dbx.sharing_list_shared_links(path=destino, direct_only=True)
                            if links.links:
                                url = links.links[0].url.replace('?dl=0', '?dl=1')
                                nuevas_fotos_urls.append({'path': destino, 'url': url})
                                if idx == 0:
                                    url_foto_perfil = url
                            else:
                                nuevas_fotos_urls.append({'path': destino, 'url': None})
                        except Exception as e3:
                            logger.warning(f"Error recuperando enlace existente en Dropbox: {e3}")
                            nuevas_fotos_urls.append({'path': destino, 'url': None})
            self.fotos_reconocimiento_urls = nuevas_fotos_urls
            self.save()
            # Guardar la URL pública en foto_perfil de Persona si existe
            # Si no hay foto_perfil, usar la primera imagen de reconocimiento facial
            if not url_foto_perfil and nuevas_fotos_urls and nuevas_fotos_urls[0].get('url'):
                url_foto_perfil = nuevas_fotos_urls[0]['url']
            print(f"[DEBUG] url_foto_perfil: {url_foto_perfil}")
            print(f"[DEBUG] nuevas_fotos_urls: {nuevas_fotos_urls}")
            if url_foto_perfil:
                print(f"[DEBUG] persona encontrada: {persona}")
                print(f"[DEBUG] persona.foto_perfil antes: {persona.foto_perfil}")
                # Convertir enlace de Dropbox a formato raw
                def dropbox_to_raw(url):
                    if url.startswith("https://www.dropbox.com/scl/fi/"):
                        url = url.replace("https://www.dropbox.com/scl/fi/", "https://dl.dropboxusercontent.com/scl/fi/")
                        url = url.replace("?dl=0", "")
                        url = url.replace("?dl=1", "")
                    return url
                raw_url = dropbox_to_raw(url_foto_perfil)
                if not persona.foto_perfil:
                    persona.foto_perfil = raw_url
                    persona.save()
                    persona.refresh_from_db()
                    print(f"[DEBUG] persona.foto_perfil después: {persona.foto_perfil}")
                print(f"[DEBUG] solicitud.foto_perfil (ImageField) no modificado")
        except Exception as e:
            logger.warning(f"Error general en Dropbox durante aprobación de solicitud: {e}")
        """Aprueba la solicitud y crea el usuario propietario"""
        from django.db import transaction
        
        try:
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
                        if rol_propietario not in usuario_existente.roles.all():
                            usuario_existente.roles.add(rol_propietario)
                    usuario = usuario_existente
                else:
                    # Crear nuevo usuario y asignar rol propietario
                    rol_propietario, _ = Rol.objects.get_or_create(
                        nombre='Propietario',
                        defaults={'descripcion': 'Propietario de vivienda'}
                    )
                    random_password = "temporal123"
                    usuario = Usuario.objects.create_user(
                        email=self.email,
                        password=random_password,
                        persona=persona,
                        estado='ACTIVO'
                    )
                    usuario.roles.add(rol_propietario)

                # 🆕 CREAR COPROPIETARIO AUTOMÁTICO para reconocimiento facial
                try:
                    from seguridad.models import Copropietarios, ReconocimientoFacial
                    
                    # Determinar número de casa: usar vivienda validada si existe, sino numero_casa
                    numero_casa_final = self.numero_casa
                    if self.vivienda_validada:
                        numero_casa_final = self.vivienda_validada.numero_casa  # ✅ Corregido
                    
                    copropietario = Copropietarios.objects.create(
                        nombres=self.nombres,
                        apellidos=self.apellidos,
                        numero_documento=self.documento_identidad,
                        email=self.email,
                        telefono=self.telefono or "000000000",
                        unidad_residencial=numero_casa_final,  # ✅ Usar el número correcto
                        tipo_residente='Propietario',
                        usuario_sistema=usuario,
                        activo=True
                    )
                    logger.info(f"Copropietario creado automáticamente: ID {copropietario.id} para usuario {usuario.email} - Casa: {numero_casa_final}")
                    
                    # 🔧 CREAR RECONOCIMIENTO FACIAL AUTOMÁTICO (usando SQL directo)
                    try:
                        from django.db import connection
                        with connection.cursor() as cursor:
                            fecha_actual = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                            sql = f"""
                            INSERT INTO reconocimiento_facial (
                                copropietario_id, 
                                proveedor_ia, 
                                vector_facial, 
                                activo, 
                                fecha_enrolamiento, 
                                fecha_modificacion, 
                                fecha_actualizacion,
                                intentos_verificacion
                            ) VALUES (
                                {copropietario.id}, 
                                'Local', 
                                '[]', 
                                1, 
                                '{fecha_actual}', 
                                '{fecha_actual}', 
                                '{fecha_actual}',
                                0
                            )
                            """
                            cursor.execute(sql)
                            reconocimiento_id = cursor.lastrowid
                            logger.info(f"ReconocimientoFacial creado automáticamente: ID {reconocimiento_id} para copropietario {copropietario.id}")
                    except Exception as e:
                        logger.warning(f"Error creando reconocimiento facial automático: {e}")
                        # No interrumpir el proceso si falla la creación del reconocimiento facial
                        
                except Exception as e:
                    logger.warning(f"Error creando copropietario automático: {e}")
                    # No interrumpir el proceso si falla la creación del copropietario

                # Actualizar solicitud
                self.estado = 'APROBADA'
                self.revisado_por = revisado_por_usuario
                self.fecha_revision = timezone.now()
                self.fecha_aprobacion = timezone.now()
                self.usuario_creado = usuario
                self.save()

                # Enviar notificación de aprobación
                try:
                    from .email_service import EmailService
                    EmailService.enviar_solicitud_aprobada(self, usuario)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Error enviando email de aprobación: {e}")

                return usuario
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[ERROR] aprobar_solicitud: {e}")
            print(f"[ERROR] aprobar_solicitud: {e}")
            raise