"""
Vista CORREGIDA para manejo de fotos de reconocimiento facial
SOLUCIONADO: Ahora busca usuarios con rol 'Propietario' en lugar de tabla Copropietarios
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.conf import settings
import os
import json
from datetime import datetime

# Importar modelos CORREGIDOS
from authz.models import Usuario, Rol
from core.utils.dropbox_upload import upload_image_to_dropbox


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_fotos_reconocimiento_corregido(request):
    """
    Endpoint CORREGIDO para subir fotos de reconocimiento facial
    URL: POST /api/authz/reconocimiento/fotos/
    
    CAMBIO: Ahora busca usuarios con rol 'Propietario' en lugar de tabla Copropietarios
    
    Payload:
    - usuario_id: ID del usuario
    - fotos: Array de archivos (máximo 5MB cada uno)
    
    Response:
    {
        "success": true,
        "data": {
            "fotos_urls": ["url1", "url2", ...],
            "total_fotos": 3,
            "mensaje": "Fotos subidas exitosamente"
        }
    }
    """
    try:
        # 1. Obtener datos del request
        usuario_id = request.data.get('usuario_id')
        fotos = request.FILES.getlist('fotos')
        
        if not usuario_id:
            return Response({
                'success': False,
                'error': 'usuario_id es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if not fotos:
            return Response({
                'success': False,
                'error': 'Debe proporcionar al menos una foto'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Validar que el usuario autenticado corresponde al usuario_id
        if str(request.user.id) != str(usuario_id):
            return Response({
                'success': False,
                'error': 'No tiene permisos para subir fotos de otro usuario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 3. CORREGIDO: Buscar usuario con rol 'Propietario' en lugar de Copropietarios
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Verificar que tenga rol de propietario
            rol_propietario = Rol.objects.filter(nombre='Propietario').first()
            if not rol_propietario or rol_propietario not in usuario.roles.all():
                return Response({
                    'success': False,
                    'error': 'El usuario no tiene rol de propietario'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Usuario.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 4. Validar que tenga persona asociada
        if not usuario.persona:
            return Response({
                'success': False,
                'error': 'El usuario no tiene perfil de persona asociado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 5. Validar fotos
        fotos_validas = []
        errores_validacion = []
        
        TIPOS_PERMITIDOS = ['image/jpeg', 'image/jpg', 'image/png']
        TAMAÑO_MAXIMO = 5 * 1024 * 1024  # 5MB
        
        for i, foto in enumerate(fotos):
            # Validar tipo de archivo
            if foto.content_type not in TIPOS_PERMITIDOS:
                errores_validacion.append(f'Foto {i+1}: Tipo de archivo no permitido. Solo JPG y PNG.')
                continue
                
            # Validar tamaño
            if foto.size > TAMAÑO_MAXIMO:
                errores_validacion.append(f'Foto {i+1}: Archivo demasiado grande. Máximo 5MB.')
                continue
                
            fotos_validas.append(foto)
        
        if errores_validacion:
            return Response({
                'success': False,
                'error': 'Errores de validación',
                'detalles': errores_validacion
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 6. Subir fotos a Dropbox
        fotos_urls = []
        carpeta_usuario = f"Propietarios/{usuario.persona.documento_identidad}"
        
        with transaction.atomic():
            for i, foto in enumerate(fotos_validas):
                try:
                    # Generar nombre único para la foto
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    nombre_archivo = f"reconocimiento_{timestamp}_{i+1}.{foto.name.split('.')[-1]}"
                    
                    # Subir a Dropbox
                    resultado = upload_image_to_dropbox(
                        foto, 
                        f"{carpeta_usuario}/{nombre_archivo}"
                    )
                    
                    # El resultado contiene {'path': '...', 'url': '...'}
                    if resultado and resultado.get('url'):
                        fotos_urls.append(resultado['url'])
                    else:
                        return Response({
                            'success': False,
                            'error': f'Error subiendo foto {i+1}: No se pudo generar URL de descarga'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                except Exception as e:
                    return Response({
                        'success': False,
                        'error': f'Error procesando foto {i+1}: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 7. CREAR REGISTRO DE RECONOCIMIENTO FACIAL EN SISTEMA DE SEGURIDAD
            try:
                from seguridad.models import ReconocimientoFacial, Copropietarios
                
                # Obtener copropietario del usuario
                copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
                
                if copropietario:
                    # Crear o actualizar registro de reconocimiento facial
                    reconocimiento, created = ReconocimientoFacial.objects.get_or_create(
                        copropietario=copropietario,
                        defaults={
                            'proveedor_ia': 'Local',
                            'vector_facial': 'temp_vector',  # Se actualizará con el procesamiento real
                            'activo': True,
                            'fotos_urls': json.dumps(fotos_urls) if hasattr(ReconocimientoFacial, 'fotos_urls') else None
                        }
                    )
                    
                    if not created:
                        # Actualizar registro existente
                        if hasattr(reconocimiento, 'fotos_urls'):
                            reconocimiento.fotos_urls = json.dumps(fotos_urls)
                        reconocimiento.activo = True
                        reconocimiento.save()
                    
                    print(f"✅ ReconocimientoFacial {'creado' if created else 'actualizado'} para copropietario {copropietario.id}")
                else:
                    print(f"❌ No se encontró copropietario para usuario {usuario.id}")
                    
            except ImportError:
                # La tabla ReconocimientoFacial no existe, continuar sin error
                print("Warning: Módulo ReconocimientoFacial no disponible")
            except Exception as e:
                # Log del error pero no fallar la operación principal
                print(f"Warning: Error guardando en ReconocimientoFacial: {e}")
        
        # 8. Respuesta exitosa
        return Response({
            'success': True,
            'data': {
                'usuario_id': usuario_id,
                'usuario_email': usuario.email,
                'propietario_nombre': f"{usuario.persona.nombre} {usuario.persona.apellido}",
                'fotos_urls': fotos_urls,
                'total_fotos': len(fotos_urls),
                'mensaje': 'Fotos de reconocimiento facial subidas exitosamente'
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_reconocimiento_facial_corregido(request):
    """
    CORREGIDO: Endpoint para consultar el estado del reconocimiento facial del usuario
    URL: GET /api/authz/reconocimiento/estado/
    """
    try:
        usuario_id = request.user.id
        
        # CORREGIDO: Buscar usuario con rol propietario
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            rol_propietario = Rol.objects.filter(nombre='Propietario').first()
            
            if not rol_propietario or rol_propietario not in usuario.roles.all():
                return Response({
                    'success': False,
                    'error': 'El usuario no tiene rol de propietario'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Usuario.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if not usuario.persona:
            return Response({
                'success': False,
                'error': 'El usuario no tiene perfil de persona asociado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar reconocimiento facial
        try:
            from seguridad.models import ReconocimientoFacial
            reconocimiento = ReconocimientoFacial.objects.get(persona_id=usuario.persona.id)
            
            fotos_urls = json.loads(reconocimiento.fotos_urls) if reconocimiento.fotos_urls else []
            
            return Response({
                'success': True,
                'data': {
                    'tiene_reconocimiento': True,
                    'estado': getattr(reconocimiento, 'estado', 'activo'),
                    'total_fotos': len(fotos_urls),
                    'fotos_urls': fotos_urls,
                    'fecha_registro': getattr(reconocimiento, 'fecha_registro', None),
                    'fecha_actualizacion': getattr(reconocimiento, 'fecha_actualizacion', None)
                }
            })
            
        except ImportError:
            return Response({
                'success': True,
                'data': {
                    'tiene_reconocimiento': False,
                    'mensaje': 'Sistema de reconocimiento facial no configurado'
                }
            })
        except:
            return Response({
                'success': True,
                'data': {
                    'tiene_reconocimiento': False,
                    'mensaje': 'No tiene fotos de reconocimiento registradas'
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_fotos_reconocimiento_corregido(request, usuario_id):
    """
    NUEVO: Endpoint para obtener fotos de reconocimiento facial del usuario
    URL: GET /api/authz/reconocimiento/fotos/{usuario_id}/
    
    Busca las fotos almacenadas en la base de datos para un propietario específico
    
    Response:
    {
        "success": true,
        "data": {
            "usuario_id": 8,
            "usuario_email": "tito@gmail.com",
            "propietario_nombre": "tito solarez",
            "fotos_urls": ["url1", "url2", ...],
            "total_fotos": 5,
            "fecha_ultima_actualizacion": "2025-09-28T03:32:12Z",
            "tiene_reconocimiento": true
        }
    }
    """
    try:
        # 1. Validar que el usuario existe y tiene rol propietario
        try:
            usuario = Usuario.objects.get(id=usuario_id)
            
            # Verificar que tenga rol de propietario
            rol_propietario = Rol.objects.filter(nombre='Propietario').first()
            if not rol_propietario or rol_propietario not in usuario.roles.all():
                return Response({
                    'success': False,
                    'error': 'El usuario no tiene rol de propietario'
                }, status=status.HTTP_403_FORBIDDEN)
                
        except Usuario.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Usuario no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 2. Verificar permisos: mismo usuario, admin o seguridad pueden ver las fotos
        if request.user.id != int(usuario_id):
            # Verificar si es admin o seguridad
            try:
                admin_role = Rol.objects.filter(nombre='Administrador').first()
                security_role = Rol.objects.filter(nombre='security').first()
                
                user_roles = request.user.roles.all()
                has_admin_role = admin_role and admin_role in user_roles
                has_security_role = security_role and security_role in user_roles
                
                if not (has_admin_role or has_security_role):
                    return Response({
                        'success': False,
                        'error': 'No tiene permisos para ver las fotos de otro usuario'
                    }, status=status.HTTP_403_FORBIDDEN)
            except:
                return Response({
                    'success': False,
                    'error': 'No tiene permisos para ver las fotos de otro usuario'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # 3. Verificar que tenga persona asociada
        if not usuario.persona:
            return Response({
                'success': False,
                'error': 'El usuario no tiene perfil de persona asociado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 4. Buscar fotos en la base de datos
        fotos_urls = []
        fecha_actualizacion = None
        tiene_reconocimiento = False
        
        try:
            from seguridad.models import ReconocimientoFacial
            
            # CORRECCIÓN: Buscar por copropietario asociado al usuario
            from seguridad.models import Copropietarios
            copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
            reconocimiento = None
            if copropietario:
                reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
            
            # Solo procesar si encontramos el reconocimiento
            if reconocimiento:
                # 🔧 CORRECCIÓN CRÍTICA: Los datos están en vector_facial
                # (el campo fotos_urls no existe en el modelo)
                if reconocimiento.vector_facial:
                    try:
                        fotos_urls = json.loads(reconocimiento.vector_facial)
                        tiene_reconocimiento = len(fotos_urls) > 0
                        fecha_actualizacion = reconocimiento.fecha_modificacion
                    except (json.JSONDecodeError, TypeError):
                        fotos_urls = []
                
                # Fallback: imagen_referencia_url
                if not fotos_urls and reconocimiento.imagen_referencia_url:
                    fotos_urls = [reconocimiento.imagen_referencia_url]
                    tiene_reconocimiento = True
                    fecha_actualizacion = reconocimiento.fecha_modificacion
            
        except ImportError:
            # Tabla ReconocimientoFacial no existe
            pass
        except:
            # ReconocimientoFacial.DoesNotExist o cualquier otro error
            pass
        
        # 5. Respuesta exitosa
        return Response({
            'success': True,
            'data': {
                'usuario_id': int(usuario_id),
                'usuario_email': usuario.email,
                'propietario_nombre': f"{usuario.persona.nombre} {usuario.persona.apellido}",
                'fotos_urls': fotos_urls,
                'total_fotos': len(fotos_urls),
                'fecha_ultima_actualizacion': fecha_actualizacion.isoformat() if fecha_actualizacion else None,
                'tiene_reconocimiento': tiene_reconocimiento
            },
            'mensaje': 'Fotos obtenidas exitosamente' if tiene_reconocimiento else 'No se encontraron fotos de reconocimiento'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)