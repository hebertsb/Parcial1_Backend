"""
Views para el panel de propietarios
Permite a los propietarios gestionar familiares e inquilinos
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import (
    FamiliarPropietario, RelacionesPropietarioInquilino, 
    SolicitudRegistroPropietario, Rol
)
from .serializers_propietario import (
    RegistroFamiliarSerializer, RegistroInquilinoSerializer,
    ListarFamiliaresSerializer, ListarInquilinosSerializer
)



class PropietarioPermissionMixin:
    """Mixin para verificar que el usuario es propietario"""
    
    def check_propietario_permission(self, user):
        """Verifica que el usuario sea propietario"""
        print(f"🔍 DEBUG: ==== VERIFICANDO PERMISOS PROPIETARIO ====")
        print(f"🔍 DEBUG: Usuario: {user.email}")
        print(f"🔍 DEBUG: Usuario autenticado: {user.is_authenticated}")
        
        try:
            # Verificar que tiene rol de propietario
            print(f"🔍 DEBUG: Verificando roles del usuario...")
            all_roles = user.roles.all()
            print(f"🔍 DEBUG: TODOS los roles del usuario: {list(all_roles.values('id', 'nombre'))}")
            
            propietario_roles = user.roles.filter(nombre='Propietario')
            print(f"🔍 DEBUG: Roles propietario query: {propietario_roles}")
            print(f"🔍 DEBUG: Cantidad de roles propietario: {propietario_roles.count()}")
            
            # También verificar si existe el rol en el sistema
            rol_propietario_exists = Rol.objects.filter(nombre='Propietario').first()
            print(f"🔍 DEBUG: ¿Existe rol 'Propietario' en el sistema?: {rol_propietario_exists}")
            
            if not propietario_roles.exists():
                print(f"❌ DEBUG: Usuario NO tiene rol de propietario")
                # Intentar asignar el rol automáticamente si falta
                print(f"🔧 DEBUG: Intentando asignar rol de propietario automáticamente...")
                if rol_propietario_exists:
                    user.roles.add(rol_propietario_exists)
                    print(f"✅ DEBUG: Rol de propietario asignado automáticamente")
                    # Volver a verificar
                    propietario_roles = user.roles.filter(nombre='Propietario')
                    if propietario_roles.exists():
                        print(f"✅ DEBUG: Verificación post-asignación exitosa")
                    else:
                        print(f"❌ DEBUG: Falló la asignación automática")
                        return False
                else:
                    print(f"❌ DEBUG: No existe el rol 'Propietario' en el sistema")
                    return False
            
            print(f"✅ DEBUG: Usuario tiene rol de propietario")
                
            # Verificar que tiene una solicitud aprobada
            print(f"🔍 DEBUG: Verificando solicitud aprobada...")
            solicitudes_all = SolicitudRegistroPropietario.objects.filter(usuario_creado=user)
            print(f"🔍 DEBUG: Todas las solicitudes del usuario: {list(solicitudes_all.values('id', 'estado', 'usuario_creado_id'))}")
            
            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=user,
                estado='APROBADA'
            ).first()
            
            print(f"🔍 DEBUG: Solicitud encontrada: {solicitud}")
            
            if solicitud is None:
                print(f"❌ DEBUG: Usuario NO tiene solicitud aprobada")
                return False
            
            print(f"✅ DEBUG: Usuario tiene solicitud aprobada (ID: {solicitud.id})")
            
            # Verificar roles otra vez para debug
            all_roles = user.roles.all()
            print(f"🔍 DEBUG: TODOS los roles del usuario: {list(all_roles.values('id', 'nombre'))}")
            
            print(f"🔍 DEBUG: ==== PERMISOS VERIFICADOS EXITOSAMENTE ====")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Error verificando permisos: {str(e)}")
            print(f"❌ DEBUG: Tipo de error: {type(e)}")
            import traceback
            print(f"❌ DEBUG: Traceback: {traceback.format_exc()}")
            return False


class GestionarFamiliaresView(APIView, PropietarioPermissionMixin):
    """Vista combinada para gestionar familiares (listar y registrar)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar familiares del propietario"""
        print(f"🔍 DEBUG: Listando familiares para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            return Response({
                'error': 'Solo los propietarios pueden ver sus familiares'
            }, status=status.HTTP_403_FORBIDDEN)
        
        familiares = FamiliarPropietario.objects.filter(
            propietario=request.user,
            activo=True
        ).order_by('-created_at')
        
        serializer = ListarFamiliaresSerializer(familiares, many=True)
        
        print(f"✅ DEBUG: Se encontraron {familiares.count()} familiares")
        
        return Response({
            'count': familiares.count(),
            'familiares': serializer.data
        })
    
    def post(self, request):
        """Registrar nuevo familiar"""
        print(f"🔍 DEBUG: Registrando familiar para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            print(f"❌ DEBUG: Usuario {request.user.email} no es propietario o no tiene solicitud aprobada")
            return Response({
                'error': 'Solo los propietarios con solicitud aprobada pueden registrar familiares'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"✅ DEBUG: Usuario {request.user.email} autorizado como propietario")
        
        serializer = RegistroFamiliarSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                familiar = serializer.save()
                print(f"✅ DEBUG: Familiar registrado exitosamente: {familiar.persona.nombre} {familiar.persona.apellido}")
                
                return Response({
                    'mensaje': 'Familiar registrado exitosamente',
                    'familiar': {
                        'id': familiar.id,
                        'nombre': familiar.persona.nombre,
                        'apellido': familiar.persona.apellido,
                        'parentesco': familiar.get_parentesco_display(),
                        'autorizado_acceso': familiar.autorizado_acceso
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"❌ DEBUG: Error al registrar familiar: {str(e)}")
                return Response({
                    'error': f'Error al registrar familiar: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"❌ DEBUG: Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GestionarInquilinosView(APIView, PropietarioPermissionMixin):
    """Vista combinada para gestionar inquilinos (listar y registrar)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar inquilinos del propietario"""
        print(f"🔍 DEBUG: Listando inquilinos para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            return Response({
                'error': 'Solo los propietarios pueden ver sus inquilinos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        inquilinos = RelacionesPropietarioInquilino.objects.filter(
            propietario=request.user,
            activo=True
        ).order_by('-created_at')
        
        serializer = ListarInquilinosSerializer(inquilinos, many=True)
        
        print(f"✅ DEBUG: Se encontraron {inquilinos.count()} inquilinos")
        
        return Response({
            'count': inquilinos.count(),
            'inquilinos': serializer.data
        })
    
    def post(self, request):
        """Registrar nuevo inquilino"""
        print(f"🔍 DEBUG: Registrando inquilino para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            print(f"❌ DEBUG: Usuario {request.user.email} no es propietario o no tiene solicitud aprobada")
            return Response({
                'error': 'Solo los propietarios con solicitud aprobada pueden registrar inquilinos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"✅ DEBUG: Usuario {request.user.email} autorizado como propietario")
        
        serializer = RegistroInquilinoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                resultado = serializer.save()
                print(f"✅ DEBUG: Inquilino registrado exitosamente: {resultado['inquilino'].email}")
                
                return Response({
                    'mensaje': resultado['mensaje'],
                    'inquilino': {
                        'id': resultado['inquilino'].id,
                        'email': resultado['inquilino'].email,
                        'nombre': resultado['inquilino'].persona.nombre if resultado['inquilino'].persona else 'N/A',
                        'password_temporal': 'inquilino123'
                    }
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"❌ DEBUG: Error al registrar inquilino: {str(e)}")
                return Response({
                    'error': f'Error al registrar inquilino: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"❌ DEBUG: Errores de validación: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuPropietarioView(APIView, PropietarioPermissionMixin):
    """Vista para obtener el menú/opciones disponibles para el propietario"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print(f"🔍 DEBUG: ==== INICIANDO MenuPropietarioView.get ====")
        print(f"🔍 DEBUG: request.path: {request.path}")
        print(f"🔍 DEBUG: request.method: {request.method}")
        print(f"🔍 DEBUG: request.user: {request.user}")
        print(f"🔍 DEBUG: request.user.is_authenticated: {request.user.is_authenticated}")
        
        print(f"🔍 DEBUG: Obteniendo menú para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        print(f"🔍 DEBUG: Verificando permisos de propietario...")
        is_propietario = self.check_propietario_permission(request.user)
        print(f"🔍 DEBUG: Es propietario: {is_propietario}")
        
        if not is_propietario:
            print(f"❌ DEBUG: Usuario NO es propietario")
            return Response({
                'error': 'Solo los propietarios pueden acceder a este menú'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"✅ DEBUG: Usuario es propietario válido")
        
        # Obtener información de la vivienda del propietario
        try:
            print(f"🔍 DEBUG: Buscando solicitud aprobada...")
            solicitud = SolicitudRegistroPropietario.objects.get(
                usuario_creado=request.user,
                estado='APROBADA'
            )
            print(f"🔍 DEBUG: Solicitud encontrada: {solicitud.id}")
            
            vivienda_info = {
                'numero_casa': solicitud.vivienda_validada.numero_casa,
                'bloque': solicitud.vivienda_validada.bloque,
                'tipo_vivienda': solicitud.vivienda_validada.tipo_vivienda
            }
            print(f"🔍 DEBUG: Vivienda info: {vivienda_info}")
        except SolicitudRegistroPropietario.DoesNotExist:
            print(f"❌ DEBUG: No se encontró solicitud aprobada")
            vivienda_info = None
        
        # Contar familiares e inquilinos actuales
        print(f"🔍 DEBUG: Contando familiares e inquilinos...")
        familiares_count = FamiliarPropietario.objects.filter(
            propietario=request.user, activo=True
        ).count()
        print(f"🔍 DEBUG: Familiares count: {familiares_count}")
        
        inquilinos_count = RelacionesPropietarioInquilino.objects.filter(
            propietario=request.user, activo=True
        ).count()
        print(f"🔍 DEBUG: Inquilinos count: {inquilinos_count}")
        
        response_data = {
            'propietario': {
                'email': request.user.email,
                'nombre_completo': f"{request.user.persona.nombre} {request.user.persona.apellido}".strip() if request.user.persona else f"{request.user.first_name} {request.user.last_name}".strip() or 'Usuario'
            },
            'vivienda': vivienda_info,
            'resumen': {
                'familiares_registrados': familiares_count,
                'inquilinos_activos': inquilinos_count
            },
            'opciones_disponibles': [
                {
                    'tipo': 'familiares',
                    'titulo': 'Registrar Familiares',
                    'descripcion': 'Registra familiares que viven en tu propiedad',
                    'endpoint': '/api/authz/propietarios/familiares/',
                    'metodo': 'POST'
                },
                {
                    'tipo': 'inquilinos',
                    'titulo': 'Registrar Inquilinos',
                    'descripcion': 'Registra inquilinos que alquilan tu propiedad',
                    'endpoint': '/api/authz/propietarios/inquilinos/',
                    'metodo': 'POST'
                },
                {
                    'tipo': 'listar_familiares',
                    'titulo': 'Ver Mis Familiares',
                    'descripcion': 'Ver lista de familiares registrados',
                    'endpoint': '/api/authz/propietarios/familiares/',
                    'metodo': 'GET'
                },
                {
                    'tipo': 'listar_inquilinos',
                    'titulo': 'Ver Mis Inquilinos',
                    'descripcion': 'Ver lista de inquilinos registrados',
                    'endpoint': '/api/authz/propietarios/inquilinos/',
                    'metodo': 'GET'
                }
            ]
        }
        
        print(f"✅ DEBUG: Response preparada exitosamente")
        print(f"🔍 DEBUG: ==== FINALIZANDO MenuPropietarioView.get ====")
        
        return Response(response_data)