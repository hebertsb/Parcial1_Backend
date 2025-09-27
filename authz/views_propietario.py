"""
Vistas para el sistema de registro de propietarios
"""
from typing import Dict, Any, Optional, cast
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import SolicitudRegistroPropietario, FamiliarPropietario, Usuario, Rol
from .serializers_propietario import (
    RegistroPropietarioInicialSerializer,
    SolicitudRegistroPropietarioSerializer,
    StatusSolicitudSerializer,
    SolicitudDetailSerializer,
    AprobarSolicitudSerializer,
    RechazarSolicitudSerializer,
    PropietarioDetalleSerializer
)
# ...existing code...

class DetallePropietarioView(APIView):
    """
    Endpoint para obtener el detalle de un propietario por ID, incluyendo:
    - Datos de Persona (foto_perfil)
    - Datos de SolicitudRegistroPropietario (foto_perfil, fotos_reconocimiento_urls)
    """
    permission_classes = [AllowAny]

    def get(self, request, propietario_id):
        from .models import Usuario, SolicitudRegistroPropietario
        usuario = Usuario.objects.filter(id=propietario_id).first()
        if not usuario or not usuario.persona:
            return Response({"error": "Propietario no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        # Buscar la solicitud asociada (la última aprobada)
        solicitud = SolicitudRegistroPropietario.objects.filter(usuario_creado=usuario).order_by('-fecha_aprobacion').first()

        serializer = PropietarioDetalleSerializer({
            "persona": usuario.persona,
            "solicitud": solicitud
        })
        return Response(serializer.data)
from .email_service import EmailService
from core.models import Vivienda, Propiedad


class RegistroPropietarioInicialView(APIView):
    """
    Vista para el registro inicial de propietarios en la plataforma
    Formulario principal para que un propietario se registre por primera vez
    """
    permission_classes = [AllowAny]
    parser_classes = [JSONParser]

    def get(self, request):
        print("🔍 GET REQUEST RECIBIDO en RegistroPropietarioInicialView")
        return Response({
            "mensaje": "Endpoint de registro de propietarios funcionando",
            "metodo_permitido": "POST",
            "campos_requeridos": [
                "primer_nombre", "primer_apellido", "cedula", "fecha_nacimiento",
                "telefono", "email", "numero_casa", "password", "confirm_password"
            ]
        })

    @extend_schema(
        request=RegistroPropietarioInicialSerializer,
        responses={
            201: OpenApiResponse(description="Registro inicial exitoso"),
            400: OpenApiResponse(description="Datos inválidos")
        },
        summary="Registro inicial de propietario",
        description="""
        Endpoint para que un propietario se registre por primera vez en la plataforma.
        Campos requeridos:
        - Información personal (nombres, apellidos, documento, fecha_nacimiento, email, telefono)
        - Número de vivienda
        - Contraseña y confirmación
        
        El sistema creará la cuenta del usuario y enviará una solicitud de aprobación al administrador.
        """
    )
    def post(self, request):
        print("🔍 DEBUG: Iniciando POST en RegistroPropietarioInicialView")
        print(f"🔍 DEBUG: request.data: {request.data}")
        
        serializer = RegistroPropietarioInicialSerializer(data=request.data)
        print(f"🔍 DEBUG: Serializer creado: {serializer}")
        
        if serializer.is_valid():
            print("🔍 DEBUG: Serializer es válido, procediendo con save()")
            try:
                with transaction.atomic():
                    print("🔍 DEBUG: Iniciando transacción atómica")
                    resultado = serializer.save()
                    print(f"🔍 DEBUG: save() exitoso, resultado: {resultado}")
                    
                    # Validar que el resultado es un diccionario
                    if not isinstance(resultado, dict):
                        raise ValueError(f"El serializer.save() retornó {type(resultado)} en lugar de dict")
                    
                    # Acceder a los elementos del diccionario con verificación de tipos
                    solicitud = resultado.get('solicitud')
                    usuario = resultado.get('usuario')
                    vivienda = resultado.get('vivienda')
                    
                    if not solicitud or not usuario or not vivienda:
                        raise ValueError("El resultado del serializer no contiene las claves esperadas")
                    
                    # Enviar notificación a administradores
                    print("🔍 DEBUG: Enviando notificación a admin")
                    self._enviar_notificacion_admin(solicitud)
                    
                    response_data = {
                        'mensaje': 'Registro realizado exitosamente',
                        'detalle': 'Su solicitud ha sido enviada para aprobación administrativa',
                        'solicitud_id': solicitud.id,
                        'estado': 'PENDIENTE',
                        'usuario_id': usuario.id,
                        'numero_vivienda': vivienda.numero_casa
                    }
                    print(f"🔍 DEBUG: Respuesta a enviar: {response_data}")
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                print(f"❌ ERROR en transaction.atomic(): {type(e).__name__}: {str(e)}")
                import traceback
                print(f"❌ TRACEBACK: {traceback.format_exc()}")
                return Response({
                    'error': 'Error interno del servidor',
                    'detalle': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print(f"❌ DEBUG: Serializer NO es válido. Errores: {serializer.errors}")
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def _enviar_notificacion_admin(self, solicitud):
        """Enviar notificación por email a administradores"""
        try:
            subject = f'Nueva Solicitud de Registro - {solicitud.nombres} {solicitud.apellidos}'
            message = f"""
            Nueva solicitud de registro de propietario:
            
            Propietario: {solicitud.nombres} {solicitud.apellidos}
            Documento: {solicitud.documento_identidad}
            Email: {solicitud.email}
            Vivienda: {solicitud.numero_casa}
            Fecha: {solicitud.created_at}
            
            Por favor, revise y apruebe/rechace esta solicitud en el panel de administración.
            """
            
            # Enviar a administradores (esto se puede configurar mejor)
            admin_emails = ['admin@condominio.com']  # Configurar en settings
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                admin_emails,
                fail_silently=True,
            )
        except Exception:
            # Log error pero no fallar el registro
            pass


class RegistroSolicitudPropietarioView(APIView):
    """
    Vista para crear solicitudes de registro de propietarios
    Endpoint público que permite a cualquier persona solicitar ser propietario
    Formato de respuesta compatible con frontend React/Next.js
    """
    permission_classes = [AllowAny]
    from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        request=SolicitudRegistroPropietarioSerializer,
        responses={
            201: OpenApiResponse(description="Solicitud creada exitosamente"),
            400: OpenApiResponse(description="Datos inválidos")
        },
        summary="Crear solicitud de registro de propietario"
    )
    def post(self, request):
        """
        Crear nueva solicitud de registro de propietario
        
        Body esperado:
        {
            "nombres": "string",
            "apellidos": "string", 
            "documento_identidad": "string",
            "email": "string",
            "telefono": "string",
            "numero_casa": "string",
            "fecha_nacimiento": "YYYY-MM-DD",
            "acepta_terminos": true,
            "password": "string",
            "confirm_password": "string"
        }
        """
        print(f"🔍 DEBUG: Datos recibidos en crear solicitud: {request.data}")
        
        # Validaciones previas
        email = request.data.get('email', '').strip()
        documento_identidad = request.data.get('documento_identidad', '').strip()
        numero_casa = request.data.get('numero_casa', '').strip()
        
        # Verificar email único
        if Usuario.objects.filter(email=email).exists():
            return Response({
                'success': False,
                'message': f'Ya existe un usuario registrado con el email {email}',
                'errors': {'email': ['Este email ya está registrado en el sistema']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar documento único
        existing_solicitud = SolicitudRegistroPropietario.objects.filter(
            documento_identidad=documento_identidad,
            estado__in=['PENDIENTE', 'EN_REVISION', 'APROBADA']
        ).first()
        
        if existing_solicitud:
            return Response({
                'success': False,
                'message': f'Ya existe una solicitud activa para el documento {documento_identidad}',
                'errors': {'documento_identidad': ['Este documento ya tiene una solicitud activa']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que la vivienda existe y está disponible
        from core.models import Vivienda, Propiedad
        
        try:
            vivienda = Vivienda.objects.get(numero_casa=numero_casa)
            
            # Verificar que no tenga propietario activo
            propietario_existente = Propiedad.objects.filter(
                vivienda=vivienda,
                tipo_tenencia='propietario',
                activo=True
            ).exists()
            
            if propietario_existente:
                return Response({
                    'success': False,
                    'message': f'La vivienda {numero_casa} ya tiene un propietario registrado',
                    'errors': {'numero_casa': ['Esta vivienda ya tiene propietario asignado']}
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Vivienda.DoesNotExist:
            return Response({
                'success': False,
                'message': f'No existe la vivienda {numero_casa} en el sistema',
                'errors': {'numero_casa': ['Esta vivienda no existe en el sistema']}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear solicitud usando el serializer
        serializer = SolicitudRegistroPropietarioSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Usar cast para indicar el tipo correcto a Pylance
                    solicitud = cast(SolicitudRegistroPropietario, serializer.save())
                    
                    # Asignar vivienda validada usando setattr para evitar problemas de tipo
                    setattr(solicitud, 'vivienda_validada', vivienda)
                    solicitud.save()
                    
                    # Enviar email de confirmación de solicitud recibida
                    EmailService.enviar_confirmacion_solicitud(solicitud, 0)
                    
                    print(f"✅ Solicitud creada exitosamente: ID={solicitud.pk}, Token={solicitud.token_seguimiento}")
                    
                    # Respuesta en formato esperado por frontend
                    return Response({
                        'success': True,
                        'message': 'Solicitud creada exitosamente',
                        'data': {
                            'id': solicitud.pk,
                            'token_seguimiento': solicitud.token_seguimiento,
                            'estado': 'pendiente'
                        }
                    }, status=status.HTTP_201_CREATED)
                    
            except Exception as e:
                print(f"❌ Error creando solicitud: {str(e)}")
                return Response({
                    'success': False,
                    'message': f'Error interno del servidor: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': False,
            'message': 'Datos inválidos',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class StatusSolicitudView(APIView):
    """
    Vista para consultar el estado de una solicitud usando el token
    Endpoint público que permite verificar el estado sin autenticación
    """
    permission_classes = [AllowAny]

    @extend_schema(
        responses={
            200: StatusSolicitudSerializer,
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Consultar estado de solicitud"
    )
    def get(self, request, token):
        try:
            solicitud = SolicitudRegistroPropietario.objects.get(token_seguimiento=token)
            serializer = StatusSolicitudSerializer(solicitud)
            return Response(serializer.data)
        except SolicitudRegistroPropietario.DoesNotExist:
            return Response({
                'error': 'Token inválido o solicitud no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)


class SolicitudesPendientesView(APIView):
    """
    Vista para listar solicitudes pendientes - Solo administradores
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: SolicitudDetailSerializer(many=True),
            403: OpenApiResponse(description="Sin permisos de administrador")
        },
        summary="Listar solicitudes pendientes"
    )
    def get(self, request):
        print("🔍 DEBUG: Iniciando GET en SolicitudesPendientesView")
        print(f"🔍 DEBUG: request.user: {request.user}")
        print(f"🔍 DEBUG: request.user.is_authenticated: {request.user.is_authenticated}")
        print(f"🔍 DEBUG: type(request.user): {type(request.user)}")
        
        # Verificar que el usuario sea administrador
        if not hasattr(request.user, 'roles'):
            print("❌ DEBUG: request.user no tiene atributo 'roles'")
            return Response({
                'error': 'Usuario no tiene roles asignados'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"🔍 DEBUG: request.user tiene roles, verificando...")
        
        try:
            admin_roles = request.user.roles.filter(nombre__in=['Administrador', 'ADMIN'])
            print(f"🔍 DEBUG: admin_roles query: {admin_roles}")
            admin_exists = admin_roles.exists()
            print(f"🔍 DEBUG: admin_exists: {admin_exists}")
        except Exception as e:
            print(f"❌ DEBUG: Error al verificar roles: {type(e).__name__}: {str(e)}")
            return Response({
                'error': f'Error al verificar permisos: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not admin_exists:
            print("❌ DEBUG: Usuario no es administrador")
            return Response({
                'error': 'No tiene permisos para acceder a este recurso'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print("✅ DEBUG: Usuario es administrador, procediendo...")
        
        try:
            print("🔍 DEBUG: Buscando solicitudes pendientes...")
            solicitudes = SolicitudRegistroPropietario.objects.filter(
                estado='PENDIENTE'
            ).order_by('-created_at')
            print(f"🔍 DEBUG: Solicitudes encontradas: {solicitudes.count()}")
            
            print("🔍 DEBUG: Serializando datos...")
            serializer = SolicitudDetailSerializer(solicitudes, many=True)
            print(f"🔍 DEBUG: Serialización completada")
            
            response_data = {
                'count': solicitudes.count(),
                'results': serializer.data
            }
            print(f"🔍 DEBUG: Preparando respuesta con {len(serializer.data)} elementos")
            
            return Response(response_data)
            
        except Exception as e:
            print(f"❌ DEBUG: Error en el procesamiento: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"❌ TRACEBACK: {traceback.format_exc()}")
            return Response({
                'error': f'Error interno: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DetalleSolicitudView(APIView):
    """
    Vista para ver el detalle completo de una solicitud - Solo administradores
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: SolicitudDetailSerializer,
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Ver detalle de solicitud"
    )
    def get(self, request, solicitud_id):
        # Verificar que el usuario sea administrador
        if not hasattr(request.user, 'roles') or not request.user.roles.filter(nombre__in=['Administrador', 'ADMIN']).exists():
            return Response({
                'error': 'No tiene permisos para acceder a este recurso'
            }, status=status.HTTP_403_FORBIDDEN)
            
        solicitud = get_object_or_404(SolicitudRegistroPropietario, id=solicitud_id)
        serializer = SolicitudDetailSerializer(solicitud)
        return Response(serializer.data)


class AprobarSolicitudView(APIView):
    """
    Vista para aprobar solicitudes - Solo administradores
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=AprobarSolicitudSerializer,
        responses={
            200: OpenApiResponse(description="Solicitud aprobada exitosamente"),
            400: OpenApiResponse(description="Error en la aprobación"),
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Aprobar solicitud de propietario"
    )
    def post(self, request, solicitud_id):
        # Verificar que el usuario sea administrador
        if not hasattr(request.user, 'roles') or not request.user.roles.filter(nombre__in=['Administrador', 'ADMIN']).exists():
            return Response({
                'error': 'No tiene permisos para acceder a este recurso'
            }, status=status.HTTP_403_FORBIDDEN)
            
        solicitud = get_object_or_404(SolicitudRegistroPropietario, id=solicitud_id)
        
        if solicitud.estado != 'PENDIENTE':
            return Response({
                'error': f'La solicitud ya fue procesada. Estado actual: {solicitud.estado}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AprobarSolicitudSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    # Usar el método del modelo que asigna el rol de propietario
                    usuario_creado = solicitud.aprobar_solicitud(request.user)
                    
                    # Actualizar observaciones si se proporcionadas
                    observaciones = ''
                    if hasattr(serializer, 'validated_data') and serializer.validated_data:
                        # Intentar obtener observaciones de forma segura
                        try:
                            if hasattr(serializer.validated_data, 'get'):
                                observaciones = str(serializer.validated_data.get('observaciones_aprobacion', ''))  # type: ignore
                        except (AttributeError, TypeError, KeyError):
                            observaciones = ''
                    if observaciones:
                        solicitud.observaciones = observaciones
                        solicitud.save()
                    
                    return Response({
                        'success': True,
                        'message': 'Solicitud aprobada y usuario creado',
                        'data': {
                            'solicitud_id': getattr(solicitud, 'id', None),
                            'nuevo_estado': 'aprobado',
                            'usuario_id': usuario_creado.id,
                            'email_propietario': usuario_creado.email,
                            'role_asignado': 'propietario',
                            'password_temporal': 'temporal123'
                        }
                    })
                        
            except Exception as e:
                return Response({
                    'error': f'Error al aprobar solicitud: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RechazarSolicitudView(APIView):
    """
    Vista para rechazar solicitudes - Solo administradores
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'roles') or not request.user.roles.filter(nombre__in=['Administrador', 'ADMIN']).exists():
            return Response({
                'error': 'No tiene permisos para acceder a este recurso'
            }, status=status.HTTP_403_FORBIDDEN)
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        request=RechazarSolicitudSerializer,
        responses={
            200: OpenApiResponse(description="Solicitud rechazada exitosamente"),
            400: OpenApiResponse(description="Error en el rechazo"),
            404: OpenApiResponse(description="Solicitud no encontrada")
        },
        summary="Rechazar solicitud de propietario"
    )
    def post(self, request, solicitud_id):
        solicitud = get_object_or_404(SolicitudRegistroPropietario, id=solicitud_id)
        
        if solicitud.estado != 'PENDIENTE':
            return Response({
                'error': f'La solicitud ya fue procesada. Estado actual: {solicitud.estado}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RechazarSolicitudSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    solicitud.estado = 'RECHAZADA'
                    motivo_rechazo = 'Sin motivo especificado'
                    if hasattr(serializer, 'validated_data') and serializer.validated_data:
                        try:
                            if hasattr(serializer.validated_data, 'get'):
                                motivo_rechazo = str(serializer.validated_data.get('motivo_rechazo', 'Sin motivo especificado'))  # type: ignore
                        except (AttributeError, TypeError, KeyError):
                            motivo_rechazo = 'Sin motivo especificado'
                    solicitud.motivo_rechazo = motivo_rechazo
                    solicitud.fecha_rechazo = timezone.now()
                    solicitud.save()
                    
                    # Enviar notificación de rechazo
                    EmailService.enviar_solicitud_rechazada(solicitud)
                    
                    return Response({
                        'success': True,
                        'message': 'Solicitud rechazada',
                        'data': {
                            'solicitud_id': solicitud.pk,
                            'nuevo_estado': 'rechazado'
                        }
                    })
                    
            except Exception as e:
                return Response({
                    'error': f'Error al rechazar solicitud: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Funciones auxiliares para notificaciones

def _enviar_notificacion_nueva_solicitud(solicitud):
    """Notifica a administradores sobre nueva solicitud"""
    try:
        # Obtener emails de administradores
        admin_emails = Usuario.objects.filter(
            roles__nombre='Administrador',
            estado='ACTIVO'
        ).values_list('email', flat=True)
        
        if admin_emails:
            # Información de la vivienda
            vivienda_info = "Vivienda no validada"
            if solicitud.vivienda_validada:
                bloque_info = f" - {solicitud.vivienda_validada.bloque}" if solicitud.vivienda_validada.bloque else ""
                vivienda_info = f"{solicitud.vivienda_validada.numero_casa}{bloque_info} ({solicitud.vivienda_validada.tipo_vivienda})"
            
            send_mail(
                subject=f'Nueva solicitud de registro - {solicitud.nombres} {solicitud.apellidos}',
                message=f"""
Nueva solicitud de registro de propietario:

Solicitante: {solicitud.nombres} {solicitud.apellidos}
Documento: {solicitud.documento_identidad}
Email: {solicitud.email}
Teléfono: {solicitud.telefono}
Vivienda solicitada: {vivienda_info}
Fecha: {solicitud.created_at}

La vivienda ha sido validada automáticamente en el sistema.

Por favor revise la solicitud en el panel de administración:
/api/auth/propietarios/admin/solicitudes/{solicitud.id}/
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=list(admin_emails)
            )
    except Exception as e:
        # Log pero no fallar
        pass


def _enviar_notificacion_aprobacion(solicitud, usuario_creado):
    """Notifica al solicitante sobre la aprobación"""
    try:
        send_mail(
            subject='Solicitud de registro aprobada',
            message=f"""
Estimado/a {solicitud.nombres} {solicitud.apellidos},

Su solicitud de registro como propietario ha sido APROBADA.

Detalles de su cuenta:
- Email: {usuario_creado.email}
- Vivienda: {solicitud.numero_casa}
- Fecha de aprobación: {solicitud.fecha_aprobacion}

Ya puede acceder al sistema del condominio.

Saludos cordiales,
Administración del Condominio
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[solicitud.email]
        )
    except Exception as e:
        # Log pero no fallar
        pass


def _enviar_notificacion_rechazo(solicitud):
    """Notifica al solicitante sobre el rechazo"""
    try:
        send_mail(
            subject='Solicitud de registro rechazada',
            message=f"""
Estimado/a {solicitud.nombres} {solicitud.apellidos},

Lamentamos informarle que su solicitud de registro como propietario ha sido RECHAZADA.

Motivo: {solicitud.motivo_rechazo}

Si considera que existe un error, puede contactar directamente con la administración.

Saludos cordiales,
Administración del Condominio
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[solicitud.email]
        )
    except Exception as e:
        # Log pero no fallar
        pass
