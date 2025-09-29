"""
Vista para manejo de fotos de reconocimiento facial
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

# Importar modelos
from seguridad.models import Copropietarios, ReconocimientoFacial
from authz.models import Usuario
from core.utils.dropbox_upload import upload_image_to_dropbox


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subir_fotos_reconocimiento(request):
    """
    Endpoint para subir fotos de reconocimiento facial
    URL: POST /api/authz/reconocimiento/fotos/
    
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
        
        # 3. Buscar copropietario asociado al usuario
        try:
            copropietario = Copropietarios.objects.get(usuario_sistema__id=usuario_id)
        except Copropietarios.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No se encontró el perfil de copropietario asociado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # 4. Validar fotos
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
        
        if not fotos_validas:
            return Response({
                'success': False,
                'error': 'No hay fotos válidas para procesar'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 5. Subir fotos a Dropbox
        dropbox_urls = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        with transaction.atomic():
            for i, foto in enumerate(fotos_validas):
                try:
                    # Generar nombre único para el archivo
                    extension = foto.name.split('.')[-1].lower()
                    nombre_archivo = f"reconocimiento_{copropietario.id}_{timestamp}_{i+1}.{extension}"
                    
                    # Subir a Dropbox en carpeta específica de reconocimiento facial
                    folder_path = f"/ReconocimientoFacial/{copropietario.id}"
                    resultado_upload = upload_image_to_dropbox(foto, nombre_archivo, folder_path)
                    
                    if resultado_upload and 'url' in resultado_upload:
                        dropbox_urls.append(resultado_upload['url'])
                    else:
                        raise Exception(f"Error subiendo foto {i+1} a Dropbox")
                        
                except Exception as e:
                    return Response({
                        'success': False,
                        'error': f'Error subiendo foto {i+1}: {str(e)}'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 6. Crear o actualizar registro de reconocimiento facial
            reconocimiento, created = ReconocimientoFacial.objects.get_or_create(
                copropietario=copropietario,
                defaults={
                    'proveedor_ia': 'Local',  # Por defecto usar reconocimiento local
                    'vector_facial': '[]',    # Vacío inicialmente, se llenará al procesar
                    'activo': True,
                    'confianza_enrolamiento': 0.0
                }
            )
            
            # 7. Actualizar URL de imagen de referencia (usar la primera foto)
            if dropbox_urls:
                reconocimiento.imagen_referencia_url = dropbox_urls[0]
                reconocimiento.activo = True
                reconocimiento.save()
            
            # 8. Generar encodings faciales (opcional, se puede hacer de forma asíncrona)
            # TODO: Implementar generación de vectores faciales en background task
            try:
                from seguridad.facial_recognition_temp import FacialRecognitionService
                
                # Procesar primera imagen para generar encoding
                primera_foto = fotos_validas[0]
                import base64
                primera_foto.seek(0)  # Resetear puntero del archivo
                imagen_base64 = base64.b64encode(primera_foto.read()).decode('utf-8')
                
                # Generar encoding (usando servicio temporal)
                encoding = FacialRecognitionService.procesar_imagen_base64(imagen_base64)
                if encoding:
                    reconocimiento.vector_facial = encoding
                    reconocimiento.confianza_enrolamiento = 85.0  # Valor simulado
                    reconocimiento.save()
                    
            except Exception as e:
                # No fallar si hay error en generación de encodings
                print(f"Advertencia: Error generando encodings faciales: {e}")
        
        # 9. Respuesta exitosa
        return Response({
            'success': True,
            'data': {
                'fotos_urls': dropbox_urls,
                'total_fotos': len(dropbox_urls),
                'mensaje': f'Se subieron {len(dropbox_urls)} fotos exitosamente para reconocimiento facial',
                'reconocimiento_activo': True,
                'usuario_id': usuario_id,
                'copropietario_id': copropietario.id
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estado_reconocimiento_facial(request):
    """
    Endpoint para consultar el estado del reconocimiento facial del usuario
    URL: GET /api/authz/reconocimiento/estado/
    """
    try:
        usuario_id = request.user.id
        
        # Buscar copropietario asociado
        try:
            copropietario = Copropietarios.objects.get(usuario_sistema__id=usuario_id)
        except Copropietarios.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No se encontró el perfil de copropietario asociado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Buscar reconocimiento facial
        try:
            reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
            
            return Response({
                'success': True,
                'data': {
                    'reconocimiento_activo': reconocimiento.activo,
                    'proveedor_ia': reconocimiento.proveedor_ia,
                    'foto_referencia': reconocimiento.imagen_referencia_url,
                    'fecha_enrolamiento': reconocimiento.fecha_enrolamiento.isoformat() if reconocimiento.fecha_enrolamiento else None,
                    'confianza': reconocimiento.confianza_enrolamiento,
                    'intentos_verificacion': reconocimiento.intentos_verificacion,
                    'ultima_verificacion': reconocimiento.ultima_verificacion.isoformat() if reconocimiento.ultima_verificacion else None
                }
            })
            
        except ReconocimientoFacial.DoesNotExist:
            return Response({
                'success': True,
                'data': {
                    'reconocimiento_activo': False,
                    'mensaje': 'No hay fotos de reconocimiento facial configuradas'
                }
            })
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error consultando estado: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def eliminar_reconocimiento_facial(request):
    """
    Endpoint para eliminar fotos de reconocimiento facial del usuario
    URL: DELETE /authz/usuarios/reconocimiento-facial/
    """
    try:
        usuario_id = request.user.id
        
        # Buscar copropietario asociado
        try:
            copropietario = Copropietarios.objects.get(usuario_sistema__id=usuario_id)
        except Copropietarios.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No se encontró el perfil de copropietario asociado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Buscar y eliminar reconocimiento facial
        try:
            reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
            
            # Desactivar en lugar de eliminar (por trazabilidad)
            reconocimiento.activo = False
            reconocimiento.save()
            
            return Response({
                'success': True,
                'data': {
                    'mensaje': 'Reconocimiento facial desactivado exitosamente'
                }
            })
            
        except ReconocimientoFacial.DoesNotExist:
            return Response({
                'success': False,
                'error': 'No hay reconocimiento facial activo para eliminar'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error eliminando reconocimiento: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)