"""
Vistas para funcionalidades administrativas
"""

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes

from .models import Usuario, Persona, Rol
from .serializers import UsuarioSerializer, PersonaSerializer
from .permissions import IsAdministrador


class CrearUsuarioSeguridadAPIView(APIView):
    """
    Vista para que los administradores creen usuarios de seguridad.
    
    Solo usuarios con rol 'Administrador' pueden crear usuarios de seguridad.
    El usuario creado tendrá rol 'Seguridad' y podrá acceder al panel de seguridad.
    """
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    @extend_schema(
        summary="Crear usuario de seguridad",
        description="""
        Permite a los administradores crear usuarios con rol de seguridad.
        
        **Funcionalidades:**
        - Crea persona con datos básicos
        - Crea usuario con email y password temporal
        - Asigna rol de 'Seguridad'
        - Genera credenciales de acceso
        
        **Restricciones:**
        - Solo administradores pueden usar este endpoint
        - El email debe ser único en el sistema
        - El documento de identidad debe ser único
        """,
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'nombres': {'type': 'string', 'example': 'Juan Carlos'},
                    'apellidos': {'type': 'string', 'example': 'Pérez González'},
                    'documento_identidad': {'type': 'string', 'example': '12345678'},
                    'email': {'type': 'string', 'format': 'email', 'example': 'seguridad@condominio.com'},
                    'telefono': {'type': 'string', 'example': '+591 70123456'},
                    'fecha_nacimiento': {'type': 'string', 'format': 'date', 'example': '1985-03-15'},
                    'genero': {'type': 'string', 'enum': ['M', 'F', 'O'], 'example': 'M'},
                    'direccion': {'type': 'string', 'example': 'Av. Principal #123'},
                    'password_temporal': {'type': 'string', 'example': 'seguridad2024', 'description': 'Password inicial (debe cambiarse en primer login)'}
                },
                'required': ['nombres', 'apellidos', 'documento_identidad', 'email']
            }
        },
        responses={
            201: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'usuario_id': {'type': 'integer'},
                            'email': {'type': 'string'},
                            'nombres_completos': {'type': 'string'},
                            'documento_identidad': {'type': 'string'},
                            'roles': {'type': 'array', 'items': {'type': 'string'}},
                            'estado': {'type': 'string'},
                            'password_temporal': {'type': 'string', 'description': 'Password que debe entregar al usuario de seguridad'},
                            'debe_cambiar_password': {'type': 'boolean'}
                        }
                    }
                }
            },
            400: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'},
                    'errores': {'type': 'object'}
                }
            },
            403: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'message': {'type': 'string'}
                }
            }
        }
    )
    def post(self, request):
        """Crear usuario de seguridad"""
        try:
            data = request.data
            
            # Validar datos requeridos
            campos_requeridos = ['nombres', 'apellidos', 'documento_identidad', 'email']
            errores = {}
            
            for campo in campos_requeridos:
                if not data.get(campo):
                    errores[campo] = f'El campo {campo} es requerido'
            
            if errores:
                return Response({
                    'success': False,
                    'message': 'Datos incompletos',
                    'errores': errores
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que no exista usuario con el mismo email
            if Usuario.objects.filter(email=data['email']).exists():
                return Response({
                    'success': False,
                    'message': f'Ya existe un usuario con el email {data["email"]}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que no exista persona con el mismo documento
            if Persona.objects.filter(documento_identidad=data['documento_identidad']).exists():
                return Response({
                    'success': False,
                    'message': f'Ya existe una persona con el documento {data["documento_identidad"]}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Password temporal (por defecto o personalizado)
            password_temporal = data.get('password_temporal', f'seg{data["documento_identidad"][:4]}2024')
            
            with transaction.atomic():
                # Crear persona
                persona = Persona.objects.create(
                    nombre=data['nombres'],
                    apellido=data['apellidos'],
                    documento_identidad=data['documento_identidad'],
                    email=data['email'],
                    telefono=data.get('telefono', ''),
                    fecha_nacimiento=data.get('fecha_nacimiento'),
                    genero=data.get('genero', ''),
                    direccion=data.get('direccion', ''),
                    tipo_persona='seguridad',
                    activo=True
                )
                
                # Crear usuario
                usuario = Usuario.objects.create_user(
                    email=data['email'],
                    password=password_temporal,
                    persona=persona,
                    estado='ACTIVO'
                )
                
                # Obtener o crear rol de seguridad
                rol_seguridad, _ = Rol.objects.get_or_create(
                    nombre='Seguridad',
                    defaults={
                        'descripcion': 'Personal de seguridad del condominio',
                        'activo': True
                    }
                )
                
                # Asignar rol
                usuario.roles.add(rol_seguridad)
                
                # Respuesta exitosa
                return Response({
                    'success': True,
                    'message': 'Usuario de seguridad creado exitosamente',
                    'data': {
                        'usuario_id': usuario.id,
                        'email': usuario.email,
                        'nombres_completos': persona.nombre_completo,
                        'documento_identidad': persona.documento_identidad,
                        'roles': [rol.nombre for rol in usuario.roles.all()],
                        'estado': usuario.estado,
                        'password_temporal': password_temporal,
                        'debe_cambiar_password': True,
                        'created_at': usuario.date_joined.isoformat()
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error interno del servidor: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListarUsuariosSeguridadAPIView(APIView):
    """
    Vista para listar todos los usuarios con rol de seguridad.
    Solo administradores pueden acceder.
    """
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    @extend_schema(
        summary="Listar usuarios de seguridad",
        description="Obtiene lista de todos los usuarios con rol de seguridad",
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'data': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'usuario_id': {'type': 'integer'},
                                'email': {'type': 'string'},
                                'nombres_completos': {'type': 'string'},
                                'documento_identidad': {'type': 'string'},
                                'telefono': {'type': 'string'},
                                'estado': {'type': 'string'},
                                'fecha_creacion': {'type': 'string'},
                                'ultimo_login': {'type': 'string', 'nullable': True}
                            }
                        }
                    },
                    'total': {'type': 'integer'}
                }
            }
        }
    )
    def get(self, request):
        """Listar usuarios de seguridad"""
        try:
            # Obtener usuarios con rol de seguridad
            usuarios_seguridad = Usuario.objects.filter(
                roles__nombre='Seguridad'
            ).select_related('persona').order_by('-date_joined')
            
            datos = []
            for usuario in usuarios_seguridad:
                datos.append({
                    'usuario_id': usuario.id,
                    'email': usuario.email,
                    'nombres_completos': usuario.persona.nombre_completo if usuario.persona else 'Sin persona asociada',
                    'documento_identidad': usuario.persona.documento_identidad if usuario.persona else '',
                    'telefono': usuario.persona.telefono if usuario.persona else '',
                    'estado': usuario.estado,
                    'fecha_creacion': usuario.date_joined.isoformat(),
                    'ultimo_login': usuario.last_login.isoformat() if usuario.last_login else None
                })
            
            return Response({
                'success': True,
                'data': datos,
                'total': len(datos)
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error obteniendo usuarios de seguridad: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ActualizarEstadoUsuarioSeguridadAPIView(APIView):
    """
    Vista para activar/desactivar usuarios de seguridad
    """
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    @extend_schema(
        summary="Actualizar estado de usuario de seguridad",
        description="Permite activar, desactivar, suspender o bloquear usuarios de seguridad",
        parameters=[
            OpenApiParameter(
                name='usuario_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID del usuario de seguridad'
            )
        ],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'estado': {
                        'type': 'string',
                        'enum': ['ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'BLOQUEADO'],
                        'example': 'ACTIVO'
                    },
                    'motivo': {
                        'type': 'string',
                        'example': 'Cambio de turno',
                        'description': 'Motivo del cambio de estado'
                    }
                },
                'required': ['estado']
            }
        }
    )
    def patch(self, request, usuario_id):
        """Actualizar estado de usuario de seguridad"""
        try:
            # Verificar que el usuario existe y tiene rol de seguridad
            usuario = Usuario.objects.filter(
                id=usuario_id,
                roles__nombre='Seguridad'
            ).first()
            
            if not usuario:
                return Response({
                    'success': False,
                    'message': 'Usuario de seguridad no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            nuevo_estado = request.data.get('estado')
            estados_validos = ['ACTIVO', 'INACTIVO', 'SUSPENDIDO', 'BLOQUEADO']
            
            if nuevo_estado not in estados_validos:
                return Response({
                    'success': False,
                    'message': f'Estado inválido. Estados válidos: {estados_validos}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            estado_anterior = usuario.estado
            usuario.estado = nuevo_estado
            usuario.save()
            
            return Response({
                'success': True,
                'message': f'Estado actualizado de {estado_anterior} a {nuevo_estado}',
                'data': {
                    'usuario_id': usuario.id,
                    'email': usuario.email,
                    'estado_anterior': estado_anterior,
                    'estado_actual': nuevo_estado,
                    'motivo': request.data.get('motivo', ''),
                    'actualizado_por': request.user.email,
                    'fecha_actualizacion': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error actualizando estado: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordSeguridadAPIView(APIView):
    """
    Vista para resetear password de usuarios de seguridad
    """
    permission_classes = [IsAuthenticated, IsAdministrador]
    
    @extend_schema(
        summary="Resetear password de usuario de seguridad",
        description="Genera un nuevo password temporal para un usuario de seguridad",
        parameters=[
            OpenApiParameter(
                name='usuario_id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='ID del usuario de seguridad'
            )
        ]
    )
    def post(self, request, usuario_id):
        """Resetear password de usuario de seguridad"""
        try:
            # Verificar que el usuario existe y tiene rol de seguridad
            usuario = Usuario.objects.filter(
                id=usuario_id,
                roles__nombre='Seguridad'
            ).first()
            
            if not usuario:
                return Response({
                    'success': False,
                    'message': 'Usuario de seguridad no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Generar nuevo password temporal
            import secrets
            import string
            password_temporal = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            
            # Actualizar password
            usuario.set_password(password_temporal)
            usuario.save()
            
            return Response({
                'success': True,
                'message': 'Password reseteado exitosamente',
                'data': {
                    'usuario_id': usuario.id,
                    'email': usuario.email,
                    'password_temporal': password_temporal,
                    'debe_cambiar_password': True,
                    'reseteado_por': request.user.email,
                    'fecha_reset': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error reseteando password: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)