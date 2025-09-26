"""
Serializers específicos para el registro de propietarios
Incluye formularios para propietarios, familiares y reconocimiento facial
"""
from typing import cast, Dict, Any, Optional
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
    Usuario, Persona, FamiliarPropietario, 
    SolicitudRegistroPropietario, Rol,
    RelacionesPropietarioInquilino
)
from core.models import Vivienda
import base64
import uuid


class RegistroPropietarioInicialSerializer(serializers.Serializer):
    """Serializer para el registro inicial de un propietario en la plataforma"""
    
    # Información de Identificación del Propietario
    primer_nombre = serializers.CharField(
        max_length=100,
        help_text="Primer nombre del propietario"
    )
    primer_apellido = serializers.CharField(
        max_length=100,
        help_text="Primer apellido del propietario"
    )
    cedula = serializers.CharField(
        max_length=20,
        help_text="Cédula de identidad"
    )
    fecha_nacimiento = serializers.DateField(
        help_text="Fecha de nacimiento (YYYY-MM-DD)"
    )
    email = serializers.EmailField(
        help_text="Correo electrónico - será su username"
    )
    telefono = serializers.CharField(
        max_length=20,
        help_text="Teléfono de contacto"
    )
    
    # Información de la Propiedad
    numero_casa = serializers.CharField(
        max_length=20,
        help_text="Número de casa o departamento"
    )
    
    # Configuración de la Cuenta
    password = serializers.CharField(
        min_length=8,
        help_text="Contraseña para la cuenta"
    )
    confirm_password = serializers.CharField(
        min_length=8,
        help_text="Confirmar contraseña"
    )
    
    # Campos opcionales
    genero = serializers.ChoiceField(
        choices=Persona.GENERO_CHOICES,
        required=False,
        allow_blank=True
    )
    
    def validate_email(self, value):
        """Validar que el email sea único"""
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya está registrado.")
        return value
    
    def validate_cedula(self, value):
        """Validar que la cédula sea única"""
        if Persona.objects.filter(documento_identidad=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada.")
        return value
    
    def validate_numero_casa(self, value):
        """Validar que la vivienda exista"""
        try:
            Vivienda.objects.get(numero_casa=value)
        except Vivienda.DoesNotExist:
            raise serializers.ValidationError(f"No existe la vivienda {value} en el sistema.")
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        # Validar que las contraseñas coincidan
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })
        
        # Validar fortaleza de la contraseña
        try:
            validate_password(attrs['password'])
        except ValidationError as e:
            raise serializers.ValidationError({'password': e.messages})
        
        return attrs
    
    def create(self, validated_data):
        """Crear la solicitud de registro inicial"""
        print("🔍 DEBUG: Iniciando create() del serializer")
        print(f"🔍 DEBUG: validated_data recibido: {validated_data}")
        try:
            # Remover campos que no van al modelo
            password = validated_data.pop('password')
            validated_data.pop('confirm_password', None)
            numero_casa = validated_data.pop('numero_casa')
            print(f"🔍 DEBUG: Campos removidos - numero_casa: {numero_casa}")

            # Eliminar fotos_base64 ANTES de cualquier uso de validated_data para modelos
            fotos_base64 = validated_data.pop('fotos_base64', None)

            # Obtener la vivienda
            print(f"🔍 DEBUG: Buscando vivienda con numero_casa: {numero_casa}")
            vivienda = Vivienda.objects.get(numero_casa=numero_casa)
            print(f"🔍 DEBUG: Vivienda encontrada: {vivienda}")

            # Crear persona
            persona_data = {
                'nombre': validated_data['primer_nombre'],
                'apellido': validated_data['primer_apellido'],
                'documento_identidad': validated_data['cedula'],
                'fecha_nacimiento': validated_data['fecha_nacimiento'],
                'telefono': validated_data['telefono'],
                'email': validated_data['email'],
                'genero': validated_data.get('genero', '')
            }
            print(f"🔍 DEBUG: Datos para crear persona: {persona_data}")
            persona = Persona.objects.create(**persona_data)
            print(f"🔍 DEBUG: Persona creada: {persona}")

            # Procesar fotos si se proporcionan
            if fotos_base64:
                self._procesar_fotos_reconocimiento(persona, fotos_base64)

            # Crear usuario
            print(f"🔍 DEBUG: Creando usuario con email: {validated_data['email']}")
            usuario = Usuario.objects.create_user(
                email=validated_data['email'],
                password=password,
                persona=persona,
                estado='ACTIVO'
            )
            print(f"🔍 DEBUG: Usuario creado: {usuario}")

            # Crear solicitud de registro con los campos correctos del modelo
            solicitud_data = {
                'nombres': validated_data['primer_nombre'],
                'apellidos': validated_data['primer_apellido'],
                'documento_identidad': validated_data['cedula'],
                'fecha_nacimiento': validated_data['fecha_nacimiento'],
                'email': validated_data['email'],
                'telefono': validated_data['telefono'],
                'numero_casa': numero_casa,
                'vivienda_validada': vivienda,
                'usuario_creado': usuario,  # ✅ AGREGAR ESTA LÍNEA
                'estado': 'PENDIENTE',
                'comentarios_admin': f"Registro inicial desde formulario web - Usuario ID: {usuario.id}"
            }
            print(f"🔍 DEBUG: Datos para crear solicitud: {solicitud_data}")

            solicitud = SolicitudRegistroPropietario.objects.create(**solicitud_data)
            print(f"🔍 DEBUG: Solicitud creada exitosamente: {solicitud}")

            resultado = {
                'usuario': usuario,
                'persona': persona,
                'solicitud': solicitud,
                'vivienda': vivienda
            }
            print(f"🔍 DEBUG: Retornando resultado: {type(resultado)}")
            return resultado
        except Exception as e:
            print(f"❌ ERROR en create(): {type(e).__name__}: {str(e)}")
            import traceback
            print(f"❌ TRACEBACK: {traceback.format_exc()}")
            raise


class FamiliarRegistroSerializer(serializers.Serializer):
    """Serializer para registrar familiares en el formulario de propietario"""
    nombres = serializers.CharField(max_length=100)
    apellidos = serializers.CharField(max_length=100)
    documento_identidad = serializers.CharField(max_length=20)
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    genero = serializers.ChoiceField(
        choices=Persona.GENERO_CHOICES, 
        required=False, 
        allow_blank=True
    )
    parentesco = serializers.ChoiceField(choices=FamiliarPropietario.PARENTESCO_CHOICES)
    parentesco_descripcion = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="Requerido si parentesco es 'otro'"
    )
    autorizado_acceso = serializers.BooleanField(default=True)
    puede_autorizar_visitas = serializers.BooleanField(default=False)
    
    # Campo para foto en base64
    fotos_base64 = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Lista de fotos en base64 para reconocimiento facial (mínimo 1, recomendado 3-5)"
    )

    def validate(self, attrs):
        # Validar que si parentesco es 'otro', se proporcione descripción
        if attrs.get('parentesco') == 'otro' and not attrs.get('parentesco_descripcion'):
            raise serializers.ValidationError({
                'parentesco_descripcion': 'Requerido cuando parentesco es "otro"'
            })
        
        # Validar documento único
        documento = attrs.get('documento_identidad')
        if documento and Persona.objects.filter(documento_identidad=documento).exists():
            raise serializers.ValidationError({
                'documento_identidad': 'Ya existe una persona con este documento'
            })
        
        return attrs


class SolicitudRegistroPropietarioSerializer(serializers.ModelSerializer):
    """Serializer para el formulario completo de registro de propietario"""
    
    # Campos adicionales para contraseña
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)  # Alias para compatibilidad con frontend
    
    # Campo para imagen de perfil (archivo)
    fotos_base64 = serializers.ListField(
        child=serializers.CharField(),
        required=True,
        help_text="Lista de fotos en base64 para reconocimiento facial (mínimo 1, recomendado 3-5)"
    )
    
    # Lista de familiares
    familiares = FamiliarRegistroSerializer(many=True, required=False)
    
    # Campos adicionales de validación
    acepta_terminos = serializers.BooleanField(write_only=True)
    acepta_tratamiento_datos = serializers.BooleanField(write_only=True)
    
    # Campos de solo lectura para mostrar información de la vivienda
    vivienda_info = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SolicitudRegistroPropietario
        fields = [
            'nombres', 'apellidos', 'documento_identidad', 'fecha_nacimiento',
            'email', 'telefono', 'numero_casa', 
            'password', 'password_confirm', 'confirm_password', 'foto_perfil', 'fotos_base64', 'familiares',
            'acepta_terminos', 'acepta_tratamiento_datos', 'vivienda_info'
        ]

    def get_vivienda_info(self, obj):
        """Retorna información de la vivienda si está validada"""
        if obj.vivienda_validada:
            return {
                'numero_casa': obj.vivienda_validada.numero_casa,
                'bloque': obj.vivienda_validada.bloque,
                'tipo_vivienda': obj.vivienda_validada.tipo_vivienda,
                'metros_cuadrados': str(obj.vivienda_validada.metros_cuadrados)
            }
        return None

    def validate_numero_casa(self, value):
        """Valida que la vivienda existe y está disponible"""
        try:
            from core.models import Vivienda, Propiedad
            
            # Verificar que la vivienda existe
            try:
                vivienda = Vivienda.objects.get(numero_casa=value)
            except Vivienda.DoesNotExist:
                raise serializers.ValidationError(
                    f"No existe la vivienda {value} en el sistema. "
                    "Verifique el número con la administración."
                )
            
            # Verificar que no hay propietario registrado
            propietario_existente = Propiedad.objects.filter(
                vivienda=vivienda,
                tipo_tenencia='propietario',
                activo=True
            ).exists()
            
            if propietario_existente:
                raise serializers.ValidationError(
                    f"La vivienda {value} ya tiene un propietario registrado en el sistema."
                )
            
            # Verificar que no hay solicitud pendiente/aprobada para esta vivienda
            solicitud_existente = SolicitudRegistroPropietario.objects.filter(
                numero_casa=value,
                estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
            ).exists()
            
            if solicitud_existente:
                raise serializers.ValidationError(
                    f"Ya existe una solicitud activa para la vivienda {value}."
                )
            
            return value
            
        except ImportError:
            # Si no se puede importar core.models, solo validar formato
            if not value or len(value.strip()) == 0:
                raise serializers.ValidationError("El número de casa es requerido")
            return value.strip().upper()

    def validate(self, attrs):
        # Validar contraseñas coincidan (soportar ambos nombres de campo)
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm') or attrs.get('confirm_password')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden',
                'confirm_password': 'Las contraseñas no coinciden'
            })
        
        # Validar documento único
        documento = attrs.get('documento_identidad')
        if documento:
            if Persona.objects.filter(documento_identidad=documento).exists():
                raise serializers.ValidationError({
                    'documento_identidad': 'Ya existe una persona registrada con este documento'
                })
            
            if SolicitudRegistroPropietario.objects.filter(
                documento_identidad=documento,
                estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
            ).exists():
                raise serializers.ValidationError({
                    'documento_identidad': 'Ya existe una solicitud activa con este documento'
                })
        
        # Validar email único
        email = attrs.get('email')
        if email:
            if Usuario.objects.filter(email=email).exists():
                raise serializers.ValidationError({
                    'email': 'Ya existe un usuario registrado con este email'
                })
            
            if SolicitudRegistroPropietario.objects.filter(
                email=email,
                estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
            ).exists():
                raise serializers.ValidationError({
                    'email': 'Ya existe una solicitud activa con este email'
                })
        
        # Validar aceptación de términos
        if not attrs.get('acepta_terminos'):
            raise serializers.ValidationError({
                'acepta_terminos': 'Debe aceptar los términos y condiciones'
            })
        
        if not attrs.get('acepta_tratamiento_datos'):
            raise serializers.ValidationError({
                'acepta_tratamiento_datos': 'Debe aceptar el tratamiento de datos personales'
            })
        
        return attrs

    def create(self, validated_data):
        # Extraer datos que no van al modelo principal
        validated_data.pop('password')
        validated_data.pop('password_confirm', None)
        validated_data.pop('confirm_password', None)
        validated_data.pop('foto_base64', None)
        validated_data.pop('familiares', [])
        validated_data.pop('acepta_terminos')
        validated_data.pop('acepta_tratamiento_datos')
        fotos_base64 = validated_data.pop('fotos_base64', None)

        # Subir fotos a Dropbox y guardar URLs
        fotos_urls = []
        if fotos_base64:
            from core.utils.dropbox_upload import upload_image_to_dropbox
            import base64
            from django.core.files.base import ContentFile
            from uuid import uuid4
            for idx, foto_b64 in enumerate(fotos_base64):
                try:
                    # Extraer extensión real del base64 (ej: data:image/png;base64,...)
                    if ';base64,' in foto_b64:
                        header, b64data = foto_b64.split(';base64,')
                        ext = header.split('/')[-1].lower()
                        if ext == 'jpeg':
                            ext = 'jpg'
                    else:
                        b64data = foto_b64
                        ext = 'jpg'
                    img_data = base64.b64decode(b64data)
                    file_name = f"solicitud_propietario_reconocimiento_{validated_data.get('documento_identidad','')}_{uuid4().hex[:8]}_{idx}.{ext}"
                    file = ContentFile(img_data, name=file_name)
                    url_foto = upload_image_to_dropbox(file, file_name, folder="/FotoPropietario")
                    fotos_urls.append(url_foto)
                except Exception:
                    pass
        validated_data['fotos_reconocimiento_urls'] = fotos_urls

        # Crear solicitud
        solicitud = SolicitudRegistroPropietario.objects.create(**validated_data)

        # Validar vivienda automáticamente
        try:
            es_valida, mensaje = solicitud.validar_vivienda()
            if not es_valida:
                # Si no es válida, eliminar la solicitud y lanzar error
                solicitud.delete()
                raise serializers.ValidationError({
                    'numero_casa': mensaje
                })
        except Exception as e:
            # Si hay error en validación, eliminar solicitud
            solicitud.delete()
            raise serializers.ValidationError({
                'numero_casa': f'Error validando vivienda: {str(e)}'
            })

        return solicitud


class PropietarioCompleteRegistrationSerializer(serializers.Serializer):
    """Serializer para completar el registro después de la aprobación"""
    
    solicitud_id = serializers.IntegerField()
    password = serializers.CharField(validators=[validate_password])
    password_confirm = serializers.CharField()
    
    # Foto para reconocimiento facial
    foto_base64 = serializers.CharField(required=False, allow_blank=True)
    
    # Familiares a registrar
    familiares = FamiliarRegistroSerializer(many=True, required=False)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden'
            })
        
        # Validar que la solicitud existe y está aprobada
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(
                id=attrs['solicitud_id'],
                estado='APROBADA'
            )
            if solicitud.usuario_creado:
                raise serializers.ValidationError({
                    'solicitud_id': 'Esta solicitud ya ha sido completada'
                })
        except SolicitudRegistroPropietario.DoesNotExist:
            raise serializers.ValidationError({
                'solicitud_id': 'Solicitud no encontrada o no aprobada'
            })
        
        attrs['solicitud'] = solicitud
        return attrs

    def save(self, **kwargs):  # type: ignore
        validated_data = cast(Dict[str, Any], getattr(self, 'validated_data', {}))
        solicitud = validated_data.get('solicitud')
        password = validated_data.get('password', '')
        foto_base64 = validated_data.get('foto_base64')
        familiares_data = validated_data.get('familiares', [])
        
        from django.db import transaction
        
        with transaction.atomic():
            # Verificar que solicitud no sea None
            if not solicitud:
                raise serializers.ValidationError("Solicitud no encontrada")
                
            # Crear persona del propietario
            persona = Persona.objects.create(
                nombre=getattr(solicitud, 'nombres', ''),
                apellido=getattr(solicitud, 'apellidos', ''),
                documento_identidad=getattr(solicitud, 'documento_identidad', ''),
                telefono=getattr(solicitud, 'telefono', ''),
                email=getattr(solicitud, 'email', ''),
                fecha_nacimiento=getattr(solicitud, 'fecha_nacimiento', None),
                tipo_persona='propietario'
            )
            
            # Procesar foto si se proporciona
            if foto_base64:
                self._procesar_foto_reconocimiento(persona, foto_base64)
            
            # Crear usuario
            usuario = Usuario.objects.create_user(
                email=getattr(solicitud, 'email', ''),
                persona=persona,
                password=password
            )
            
            # Asignar rol de propietario
            rol_propietario, _ = Rol.objects.get_or_create(
                nombre='Propietario',
                defaults={'descripcion': 'Propietario de vivienda'}
            )
            usuario.roles.add(rol_propietario)
            
            # Crear familiares
            for familiar_data in familiares_data:
                self._crear_familiar(usuario, familiar_data)
            
            # Actualizar solicitud
            if hasattr(solicitud, 'usuario_creado') and hasattr(solicitud, 'save'):
                solicitud.usuario_creado = usuario  # type: ignore
                solicitud.save()  # type: ignore
            
            return usuario

    def _procesar_fotos_reconocimiento(self, persona, fotos_base64):
        """Procesa varias fotos para reconocimiento facial y guarda todos los encodings"""
        try:
            from django.core.files.base import ContentFile
            import base64
            from core.utils.face_encoding import generate_face_encoding_from_base64
            encodings = []
            for idx, foto_base64 in enumerate(fotos_base64):
                # Decodificar base64 y guardar la primera foto como perfil
                if idx == 0:
                    format_str, imgstr = foto_base64.split(';base64,')
                    ext = format_str.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'perfil_{persona.documento_identidad}.{ext}')
                    persona.foto_perfil = data
                encoding = generate_face_encoding_from_base64(foto_base64)
                if encoding:
                    encodings.append(encoding)
            if encodings:
                persona.encoding_facial = encodings
                persona.reconocimiento_facial_activo = True
            persona.save()
        except Exception as e:
            pass

    def _crear_familiar(self, propietario, familiar_data):
        """Crea un familiar del propietario"""
        foto_base64 = familiar_data.pop('foto_base64', None)
        
        # Crear persona del familiar
        persona = Persona.objects.create(
            nombre=familiar_data['nombres'],
            apellido=familiar_data['apellidos'],
            documento_identidad=familiar_data['documento_identidad'],
            telefono=familiar_data.get('telefono', ''),
            email=familiar_data.get('email', ''),
            fecha_nacimiento=familiar_data['fecha_nacimiento'],
            genero=familiar_data.get('genero', ''),
            tipo_persona='familiar'
        )
        
        # Procesar fotos si se proporcionan
        
        # Crear relación familiar
        FamiliarPropietario.objects.create(
            propietario=propietario,
            persona=persona,
            parentesco=familiar_data['parentesco'],
            parentesco_descripcion=familiar_data.get('parentesco_descripcion', ''),
            autorizado_acceso=familiar_data.get('autorizado_acceso', True),
            puede_autorizar_visitas=familiar_data.get('puede_autorizar_visitas', False)
        )


class SolicitudRegistroDetailSerializer(serializers.ModelSerializer):
    """Serializer para mostrar detalles de solicitud al administrador"""
    
    revisado_por_nombre = serializers.CharField(
        source='revisado_por.persona.nombre_completo',
        read_only=True
    )
    
    class Meta:
        model = SolicitudRegistroPropietario
        fields = '__all__'


class SolicitudRegistroUpdateSerializer(serializers.ModelSerializer):
    """Serializer para que el administrador actualice solicitudes"""
    
    class Meta:
        model = SolicitudRegistroPropietario
        fields = ['estado', 'comentarios_admin']
    
    def update(self, instance, validated_data):
        # Marcar fecha de revisión si cambia estado
        if 'estado' in validated_data and validated_data['estado'] != instance.estado:
            validated_data['fecha_revision'] = timezone.now()
            validated_data['revisado_por'] = self.context['request'].user
        
        return super().update(instance, validated_data)


class StatusSolicitudSerializer(serializers.ModelSerializer):
    """Serializer para consultar el estado de una solicitud con token"""
    
    solicitud_id = serializers.SerializerMethodField()
    vivienda_info = serializers.SerializerMethodField()
    familiares_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SolicitudRegistroPropietario
        fields = [
            'solicitud_id', 'estado', 'nombres', 'apellidos', 
            'numero_casa', 'created_at', 'vivienda_info', 'familiares_count'
        ]
    
    def get_solicitud_id(self, obj):
        return obj.id
    
    def get_vivienda_info(self, obj):
        if obj.vivienda_validada:
            return {
                'numero_casa': obj.vivienda_validada.numero_casa,
                'bloque': obj.vivienda_validada.bloque,
                'tipo_vivienda': obj.vivienda_validada.tipo_vivienda
            }
        return None
    
    def get_familiares_count(self, obj):
        return FamiliarPropietario.objects.filter(solicitud=obj).count()


class SolicitudDetailSerializer(serializers.ModelSerializer):
    """Serializer para mostrar detalles completos de solicitud a administradores"""
    
    vivienda_info = serializers.SerializerMethodField()
    familiares_count = serializers.SerializerMethodField()
    familiares = serializers.SerializerMethodField()
    revisado_por_info = serializers.SerializerMethodField()
    foto_perfil = serializers.ImageField(read_only=True)
    
    class Meta:
        model = SolicitudRegistroPropietario
        fields = [
            'id', 'nombres', 'apellidos', 'documento_identidad', 'email',
            'telefono', 'numero_casa', 'fecha_nacimiento', 'estado', 'created_at', 'fecha_revision',
            'comentarios_admin', 'revisado_por_info', 'vivienda_info', 'familiares_count', 'familiares',
            'foto_perfil'
        ]
    
    def get_vivienda_info(self, obj):
        if obj.vivienda_validada:
            return {
                'numero_casa': obj.vivienda_validada.numero_casa,
                'bloque': obj.vivienda_validada.bloque,
                'tipo_vivienda': obj.vivienda_validada.tipo_vivienda,
                'metros_cuadrados': str(obj.vivienda_validada.metros_cuadrados),
                'estado': obj.vivienda_validada.estado
            }
        return None
    
    def get_revisado_por_info(self, obj):
        if obj.revisado_por:
            return {
                'email': obj.revisado_por.email,
                'nombre_completo': f"{obj.revisado_por.first_name} {obj.revisado_por.last_name}".strip() or obj.revisado_por.email
            }
        return None
    
    def get_familiares_count(self, obj):
        # Si la solicitud ya fue aprobada y se creó el usuario, mostrar familiares
        if obj.usuario_creado:
            return FamiliarPropietario.objects.filter(propietario=obj.usuario_creado).count()
        return 0
    
    def get_familiares(self, obj):
        # Si la solicitud ya fue aprobada y se creó el usuario, mostrar familiares
        if obj.usuario_creado:
            familiares = FamiliarPropietario.objects.filter(propietario=obj.usuario_creado)
            return [{
                'nombres': getattr(f.persona, 'nombre', 'N/A'),
                'apellidos': getattr(f.persona, 'apellido', 'N/A'),
                'documento_identidad': getattr(f.persona, 'documento_identidad', 'N/A'),
                'parentesco': getattr(f, 'get_parentesco_display', lambda: f.parentesco)(),
                'telefono': getattr(f.persona, 'telefono', 'N/A')
            } for f in familiares]
        return []


class AprobarSolicitudSerializer(serializers.Serializer):
    """Serializer para aprobar solicitudes"""
    
    observaciones_aprobacion = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Observaciones opcionales sobre la aprobación"
    )


class RechazarSolicitudSerializer(serializers.Serializer):
    """Serializer para rechazar solicitudes"""
    
    motivo_rechazo = serializers.CharField(
        required=True,
        help_text="Motivo del rechazo de la solicitud"
    )


# ==================== SERIALIZERS PARA PROPIETARIOS ====================

class RegistroFamiliarSerializer(serializers.ModelSerializer):
    """Serializer para que propietarios registren familiares"""
    
    # Datos de la persona (familiar)
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    documento_identidad = serializers.CharField(max_length=20)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField()
    fecha_nacimiento = serializers.DateField()
    
    class Meta:
        model = FamiliarPropietario
        fields = [
            'nombre', 'apellido', 'documento_identidad', 'telefono', 'email', 
            'fecha_nacimiento', 'parentesco', 'parentesco_descripcion',
            'autorizado_acceso', 'puede_autorizar_visitas', 'observaciones'
        ]
        
    def validate_documento_identidad(self, value):
        """Validar que el documento no esté ya registrado"""
        if Persona.objects.filter(documento_identidad=value).exists():
            raise serializers.ValidationError("Ya existe una persona con este documento de identidad.")
        return value
        
    def validate_email(self, value):
        """Validar que el email no esté ya registrado"""
        if Persona.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe una persona con este email.")
        return value
    
    def create(self, validated_data):
        # Extraer datos de persona
        persona_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido': validated_data.pop('apellido'),
            'documento_identidad': validated_data.pop('documento_identidad'),
            'telefono': validated_data.get('telefono', ''),
            'email': validated_data.pop('email'),
            'fecha_nacimiento': validated_data.pop('fecha_nacimiento'),
            'tipo_persona': 'familiar'
        }
        
        # Crear la persona
        persona = Persona.objects.create(**persona_data)
        
        # Crear la relación familiar
        familiar = FamiliarPropietario.objects.create(
            persona=persona,
            propietario=self.context['request'].user,
            **validated_data
        )
        
        return familiar


class RegistroInquilinoSerializer(serializers.Serializer):
    """Serializer para que propietarios registren inquilinos"""
    
    # Datos de la persona (inquilino)
    nombre = serializers.CharField(max_length=100)
    apellido = serializers.CharField(max_length=100)
    documento_identidad = serializers.CharField(max_length=20)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
    email = serializers.EmailField()
    fecha_nacimiento = serializers.DateField()
    
    # Datos de la relación de alquiler
    fecha_inicio = serializers.DateField()
    fecha_fin = serializers.DateField(required=False, allow_null=True)
    monto_alquiler = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, allow_null=True)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_documento_identidad(self, value):
        """Validar que el documento no esté ya registrado"""
        if Persona.objects.filter(documento_identidad=value).exists():
            raise serializers.ValidationError("Ya existe una persona con este documento de identidad.")
        return value
        
    def validate_email(self, value):
        """Validar que el email no esté ya registrado como persona"""
        if Persona.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe una persona con este email.")
        # Validar que no esté registrado como usuario
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        fecha_inicio = attrs.get('fecha_inicio')
        fecha_fin = attrs.get('fecha_fin')
        
        if fecha_fin and fecha_inicio and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha de fin debe ser posterior a la fecha de inicio.'
            })
            
        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        propietario = request.user
        
        # Obtener la vivienda del propietario (asumimos que tiene una vivienda principal)
        # Esto puedes ajustarlo según tu lógica de negocio
        try:
            # Buscar la vivienda del propietario en el modelo SolicitudRegistroPropietario aprobada
            solicitud = SolicitudRegistroPropietario.objects.get(
                usuario_creado=propietario,
                estado='APROBADA'
            )
            vivienda = solicitud.vivienda_validada
            
            if not vivienda:
                raise serializers.ValidationError("No se encontró una vivienda asociada al propietario.")
                
        except SolicitudRegistroPropietario.DoesNotExist:
            raise serializers.ValidationError("No se encontró una solicitud aprobada para este propietario.")
        
        # Extraer datos de persona y relación
        persona_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido': validated_data.pop('apellido'),
            'documento_identidad': validated_data.pop('documento_identidad'),
            'telefono': validated_data.get('telefono', ''),
            'email': validated_data.pop('email'),
            'fecha_nacimiento': validated_data.pop('fecha_nacimiento'),
            'tipo_persona': 'inquilino'
        }
        
        relacion_data = validated_data  # Lo que queda son datos de la relación
        
        try:
            with transaction.atomic():
                # Crear la persona
                persona = Persona.objects.create(**persona_data)
                
                # Crear usuario para el inquilino
                usuario_inquilino = Usuario.objects.create_user(
                    email=persona.email,
                    password='inquilino123',  # Password temporal
                    tipo_usuario='inquilino'
                )
                
                # Asignar rol de inquilino
                rol_inquilino, _ = Rol.objects.get_or_create(nombre='Inquilino')
                usuario_inquilino.roles.add(rol_inquilino)
                
                # Crear persona para el usuario
                persona_usuario = Persona.objects.create(
                    nombre=persona.nombre,
                    apellido=persona.apellido,
                    documento_identidad=persona.documento_identidad + '_USER',  # Diferenciador
                    telefono=persona.telefono,
                    email=persona.email,
                    fecha_nacimiento=persona.fecha_nacimiento,
                    tipo_persona='inquilino'
                )
                usuario_inquilino.persona = persona_usuario
                usuario_inquilino.save()
                
                # Crear la relación propietario-inquilino
                relacion = RelacionesPropietarioInquilino.objects.create(
                    propietario=propietario,
                    inquilino=usuario_inquilino,
                    vivienda=vivienda,
                    **relacion_data
                )
                
                return {
                    'inquilino': usuario_inquilino,
                    'relacion': relacion,
                    'mensaje': 'Inquilino registrado exitosamente. Password temporal: inquilino123'
                }
                
        except Exception as e:
            raise serializers.ValidationError(f"Error al crear el inquilino: {str(e)}")


class ListarFamiliaresSerializer(serializers.ModelSerializer):
    """Serializer para listar familiares del propietario"""
    
    persona_info = serializers.SerializerMethodField()
    parentesco_display = serializers.CharField(source='get_parentesco_display', read_only=True)
    
    class Meta:
        model = FamiliarPropietario
        fields = [
            'id', 'parentesco', 'parentesco_display', 'parentesco_descripcion',
            'autorizado_acceso', 'puede_autorizar_visitas', 'observaciones',
            'activo', 'created_at', 'persona_info'
        ]
    
    def get_persona_info(self, obj):
        return {
            'nombre': obj.persona.nombre,
            'apellido': obj.persona.apellido,
            'documento_identidad': obj.persona.documento_identidad,
            'telefono': obj.persona.telefono,
            'email': obj.persona.email,
            'fecha_nacimiento': obj.persona.fecha_nacimiento
        }


class ListarInquilinosSerializer(serializers.ModelSerializer):
    """Serializer para listar inquilinos del propietario"""
    
    inquilino_info = serializers.SerializerMethodField()
    vivienda_info = serializers.SerializerMethodField()
    
    class Meta:
        model = RelacionesPropietarioInquilino
        fields = [
            'id', 'fecha_inicio', 'fecha_fin', 'activo', 'monto_alquiler',
            'observaciones', 'created_at', 'inquilino_info', 'vivienda_info'
        ]
    
    def get_inquilino_info(self, obj):
        if obj.inquilino.persona:
            return {
                'nombre': obj.inquilino.persona.nombre,
                'apellido': obj.inquilino.persona.apellido,
                'documento_identidad': obj.inquilino.persona.documento_identidad,
                'telefono': obj.inquilino.persona.telefono,
                'email': obj.inquilino.email
            }
        return {'email': obj.inquilino.email}
    
    def get_vivienda_info(self, obj):
        return {
            'numero_casa': obj.vivienda.numero_casa,
            'bloque': obj.vivienda.bloque,
            'tipo_vivienda': obj.vivienda.tipo_vivienda
        }
