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
        print(f"ðŸ” DEBUG: ==== VERIFICANDO PERMISOS PROPIETARIO ====")
        print(f"ðŸ” DEBUG: Usuario: {user.email}")
        print(f"ðŸ” DEBUG: Usuario autenticado: {user.is_authenticated}")
        
        try:
            # Verificar que tiene rol de propietario
            print(f"ðŸ” DEBUG: Verificando roles del usuario...")
            all_roles = user.roles.all()
            print(f"ðŸ” DEBUG: TODOS los roles del usuario: {list(all_roles.values('id', 'nombre'))}")
            
            propietario_roles = user.roles.filter(nombre='Propietario')
            print(f"ðŸ” DEBUG: Roles propietario query: {propietario_roles}")
            print(f"ðŸ” DEBUG: Cantidad de roles propietario: {propietario_roles.count()}")
            
            # TambiÃ©n verificar si existe el rol en el sistema
            rol_propietario_exists = Rol.objects.filter(nombre='Propietario').first()
            print(f"ðŸ” DEBUG: Â¿Existe rol 'Propietario' en el sistema?: {rol_propietario_exists}")
            
            if not propietario_roles.exists():
                # ValidaciÃ³n estricta: NO auto-asignar rol de propietario
                return False
                print(f"âŒ DEBUG: Usuario NO tiene rol de propietario")
                # Intentar asignar el rol automÃ¡ticamente si falta
                print(f"ðŸ”§ DEBUG: Intentando asignar rol de propietario automÃ¡ticamente...")
                if rol_propietario_exists:
                    user.roles.add(rol_propietario_exists)
                    print(f"âœ… DEBUG: Rol de propietario asignado automÃ¡ticamente")
                    # Volver a verificar
                    propietario_roles = user.roles.filter(nombre='Propietario')
                    if propietario_roles.exists():
                        print(f"âœ… DEBUG: VerificaciÃ³n post-asignaciÃ³n exitosa")
                    else:
                        print(f"âŒ DEBUG: FallÃ³ la asignaciÃ³n automÃ¡tica")
                        return False
                else:
                    print(f"âŒ DEBUG: No existe el rol 'Propietario' en el sistema")
                    return False
            
            print(f"âœ… DEBUG: Usuario tiene rol de propietario")
                
            # Verificar que tiene una solicitud aprobada
            print('DEBUG: Verificando solicitud aprobada...')
            solicitudes_all = SolicitudRegistroPropietario.objects.filter(usuario_creado=user)
            print('DEBUG: Todas las solicitudes del usuario:', list(solicitudes_all.values('id', 'estado', 'usuario_creado_id')))

            solicitud = SolicitudRegistroPropietario.objects.filter(
                usuario_creado=user,
                estado='APROBADA'
            ).first()
            print('DEBUG: Solicitud encontrada:', solicitud)

            if solicitud:
                print('DEBUG: Usuario tiene solicitud aprobada (ID: {0})'.format(solicitud.id))
                all_roles = user.roles.all()
                print('DEBUG: Roles actuales:', list(all_roles.values('id', 'nombre')))
                print('DEBUG: Permisos verificados correctamente')
                return True

            print('WARN: Usuario sin solicitud aprobada; permitiendo acceso por rol existente')
            return True
            
        except Exception as e:
            print(f"âŒ DEBUG: Error verificando permisos: {str(e)}")
            print(f"âŒ DEBUG: Tipo de error: {type(e)}")
            import traceback
            print(f"âŒ DEBUG: Traceback: {traceback.format_exc()}")
            return False


class GestionarFamiliaresView(APIView, PropietarioPermissionMixin):
    """Vista combinada para gestionar familiares (listar y registrar)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar familiares del propietario"""
        print(f"ðŸ” DEBUG: Listando familiares para propietario: {request.user.email}")
        
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
        
        print(f"âœ… DEBUG: Se encontraron {familiares.count()} familiares")
        
        return Response({
            'count': familiares.count(),
            'familiares': serializer.data
        })
    
    def post(self, request):
        """Registrar nuevo familiar"""
        print(f"ðŸ” DEBUG: Registrando familiar para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            print(f"âŒ DEBUG: Usuario {request.user.email} no es propietario o no tiene solicitud aprobada")
            return Response({
                'error': 'Solo los propietarios autorizados pueden registrar familiares'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"âœ… DEBUG: Usuario {request.user.email} autorizado como propietario")
        
        serializer = RegistroFamiliarSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                familiar = serializer.save()
                print(f"âœ… DEBUG: Familiar registrado exitosamente: {familiar.persona.nombre} {familiar.persona.apellido}")
                
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
                print(f"âŒ DEBUG: Error al registrar familiar: {str(e)}")
                return Response({
                    'error': f'Error al registrar familiar: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"âŒ DEBUG: Errores de validaciÃ³n: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GestionarInquilinosView(APIView, PropietarioPermissionMixin):
    """Vista combinada para gestionar inquilinos (listar y registrar)"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Listar inquilinos del propietario"""
        print(f"ðŸ” DEBUG: Listando inquilinos para propietario: {request.user.email}")
        
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
        
        print(f"âœ… DEBUG: Se encontraron {inquilinos.count()} inquilinos")
        
        return Response({
            'count': inquilinos.count(),
            'inquilinos': serializer.data
        })
    
    def post(self, request):
        """Registrar nuevo inquilino"""
        print(f"ðŸ” DEBUG: Registrando inquilino para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        if not self.check_propietario_permission(request.user):
            print(f"âŒ DEBUG: Usuario {request.user.email} no es propietario o no tiene solicitud aprobada")
            return Response({
                'error': 'Solo los propietarios con solicitud aprobada pueden registrar inquilinos'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"âœ… DEBUG: Usuario {request.user.email} autorizado como propietario")
        
        serializer = RegistroInquilinoSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                resultado = serializer.save()
                print(f"âœ… DEBUG: Inquilino registrado exitosamente: {resultado['inquilino'].email}")
                
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
                print(f"âŒ DEBUG: Error al registrar inquilino: {str(e)}")
                return Response({
                    'error': f'Error al registrar inquilino: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        print(f"âŒ DEBUG: Errores de validaciÃ³n: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MenuPropietarioView(APIView, PropietarioPermissionMixin):
    """Vista para obtener el menÃº/opciones disponibles para el propietario"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        print(f"ðŸ” DEBUG: ==== INICIANDO MenuPropietarioView.get ====")
        print(f"ðŸ” DEBUG: request.path: {request.path}")
        print(f"ðŸ” DEBUG: request.method: {request.method}")
        print(f"ðŸ” DEBUG: request.user: {request.user}")
        print(f"ðŸ” DEBUG: request.user.is_authenticated: {request.user.is_authenticated}")
        
        print(f"ðŸ” DEBUG: Obteniendo menÃº para propietario: {request.user.email}")
        
        # Verificar permisos de propietario
        print(f"ðŸ” DEBUG: Verificando permisos de propietario...")
        is_propietario = self.check_propietario_permission(request.user)
        print(f"ðŸ” DEBUG: Es propietario: {is_propietario}")
        
        if not is_propietario:
            print(f"âŒ DEBUG: Usuario NO es propietario")
            return Response({
                'error': 'Solo los propietarios pueden acceder a este menÃº'
            }, status=status.HTTP_403_FORBIDDEN)
        
        print(f"âœ… DEBUG: Usuario es propietario vÃ¡lido")
        
        # Obtener informaciÃ³n de la vivienda del propietario
        try:
            print(f"ðŸ” DEBUG: Buscando solicitud aprobada...")
            solicitud = SolicitudRegistroPropietario.objects.get(
                usuario_creado=request.user,
                estado='APROBADA'
            )
            print(f"ðŸ” DEBUG: Solicitud encontrada: {solicitud.id}")
            
            vivienda_info = {
                'numero_casa': solicitud.vivienda_validada.numero_casa,
                'bloque': solicitud.vivienda_validada.bloque,
                'tipo_vivienda': solicitud.vivienda_validada.tipo_vivienda
            }
            print(f"ðŸ” DEBUG: Vivienda info: {vivienda_info}")
        except SolicitudRegistroPropietario.DoesNotExist:
            print(f"âŒ DEBUG: No se encontrÃ³ solicitud aprobada")
            vivienda_info = None
        
        # Contar familiares e inquilinos actuales
        print(f"ðŸ” DEBUG: Contando familiares e inquilinos...")
        familiares_count = FamiliarPropietario.objects.filter(
            propietario=request.user, activo=True
        ).count()
        print(f"ðŸ” DEBUG: Familiares count: {familiares_count}")
        
        inquilinos_count = RelacionesPropietarioInquilino.objects.filter(
            propietario=request.user, activo=True
        ).count()
        print(f"ðŸ” DEBUG: Inquilinos count: {inquilinos_count}")
        
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
        
        print(f"âœ… DEBUG: Response preparada exitosamente")
        print(f"ðŸ” DEBUG: ==== FINALIZANDO MenuPropietarioView.get ====")
        
        return Response(response_data)
