"""
Vista mejorada para el panel de propietarios con Dropbox siguiendo el mismo flujo exitoso
que implementamos para las solicitudes de registro.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.parsers import JSONParser
from django.db import transaction
import json
import base64
import uuid
from datetime import datetime
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


class SubirFotoPropietarioDropboxView(APIView):
    """
    Vista mejorada para subir fotos del propietario usando el mismo flujo exitoso
    que implementamos para las solicitudes con Dropbox.
    
    Recibe fotos en formato base64 y las procesa de manera consistente.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    
    @extend_schema(
        summary="Subir fotos de reconocimiento facial (Panel Propietario)",
        description="Permite al propietario subir fotos para reconocimiento facial usando el flujo optimizado con Dropbox",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'fotos_base64': {
                        'type': 'array',
                        'items': {'type': 'string'},
                        'description': 'Array de imágenes en formato base64'
                    }
                },
                'required': ['fotos_base64']
            }
        },
        responses={
            200: OpenApiResponse(description="Fotos subidas correctamente"),
            400: OpenApiResponse(description="Error en los datos enviados"),
            404: OpenApiResponse(description="Propietario no encontrado"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def post(self, request):
        """Subir nuevas fotos de reconocimiento facial para propietario autenticado"""
        
        print("🎯 [PANEL PROPIETARIO] Iniciando proceso de subida de fotos...")
        
        try:
            # 1. Obtener datos del request
            fotos_base64 = request.data.get('fotos_base64', [])
            usuario = request.user
            
            print(f"📊 [PANEL PROPIETARIO] Usuario: {usuario.email}")
            print(f"📸 [PANEL PROPIETARIO] Fotos recibidas: {len(fotos_base64)}")
            
            # 2. Validaciones básicas
            if not fotos_base64:
                return Response({
                    'success': False,
                    'error': 'Se requiere al menos una foto en formato base64'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not isinstance(fotos_base64, list):
                return Response({
                    'success': False,
                    'error': 'fotos_base64 debe ser un array'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Importar modelos necesarios
            from seguridad.models import Copropietarios, ReconocimientoFacial
            from core.utils.dropbox_upload import upload_image_to_dropbox
            
            # 4. Buscar copropietario asociado al usuario
            try:
                copropietario = Copropietarios.objects.get(usuario_sistema_id=usuario.id)
                documento_identidad = copropietario.numero_documento or str(usuario.id)
                print(f"✅ [PANEL PROPIETARIO] Copropietario encontrado: {copropietario.nombres} {copropietario.apellidos}")
                print(f"📄 [PANEL PROPIETARIO] Documento: {documento_identidad}")
            except Copropietarios.DoesNotExist:
                print("❌ [PANEL PROPIETARIO] No se encontró copropietario para este usuario")
                return Response({
                    'success': False,
                    'error': 'No se encontró información de copropietario para este usuario'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 5. Procesar cada foto base64
            fotos_urls_subidas = []
            errores_procesamiento = []
            
            with transaction.atomic():
                for idx, foto_base64 in enumerate(fotos_base64):
                    try:
                        print(f"🔄 [PANEL PROPIETARIO] Procesando foto {idx + 1}/{len(fotos_base64)}...")
                        
                        # Limpiar formato base64
                        if ',' in foto_base64:
                            foto_base64 = foto_base64.split(',', 1)[1]
                        
                        # Decodificar base64
                        try:
                            img_data = base64.b64decode(foto_base64)
                        except Exception as e:
                            error_msg = f"Error decodificando base64 en foto {idx + 1}: {str(e)}"
                            print(f"❌ [PANEL PROPIETARIO] {error_msg}")
                            errores_procesamiento.append(error_msg)
                            continue
                        
                        # Validar que es una imagen válida
                        try:
                            img = Image.open(BytesIO(img_data))
                            img.verify()
                            print(f"✅ [PANEL PROPIETARIO] Foto {idx + 1} validada: {img.format} {img.size}")
                        except Exception as e:
                            error_msg = f"Imagen inválida en foto {idx + 1}: {str(e)}"
                            print(f"❌ [PANEL PROPIETARIO] {error_msg}")
                            errores_procesamiento.append(error_msg)
                            continue
                        
                        # Generar nombre único para el archivo
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        unique_id = uuid.uuid4().hex[:8]
                        nombre_archivo = f"propietario_panel_{documento_identidad}_{timestamp}_{unique_id}_{idx}.jpg"
                        
                        # Crear archivo temporal para subir
                        file_content = ContentFile(img_data, name=nombre_archivo)
                        
                        # Subir a Dropbox usando la misma estructura que las solicitudes aprobadas
                        carpeta_propietario = f"/Propietarios/{documento_identidad}"
                        
                        print(f"📤 [PANEL PROPIETARIO] Subiendo foto {idx + 1} a: {carpeta_propietario}/{nombre_archivo}")
                        
                        resultado_upload = upload_image_to_dropbox(
                            file_content, 
                            nombre_archivo, 
                            carpeta_propietario
                        )
                        
                        if resultado_upload and resultado_upload.get('url'):
                            foto_url = resultado_upload['url']
                            fotos_urls_subidas.append(foto_url)
                            print(f"✅ [PANEL PROPIETARIO] Foto {idx + 1} subida exitosamente: {foto_url[:80] if foto_url else 'URL no disponible'}...")
                        else:
                            error_msg = f"Error en upload de foto {idx + 1} a Dropbox"
                            print(f"❌ [PANEL PROPIETARIO] {error_msg}")
                            errores_procesamiento.append(error_msg)
                        
                    except Exception as e:
                        error_msg = f"Error procesando foto {idx + 1}: {str(e)}"
                        print(f"❌ [PANEL PROPIETARIO] {error_msg}")
                        errores_procesamiento.append(error_msg)
                
                # 6. Actualizar o crear registro de reconocimiento facial
                if fotos_urls_subidas:
                    reconocimiento, created = ReconocimientoFacial.objects.get_or_create(
                        copropietario=copropietario,
                        defaults={
                            'proveedor_ia': 'Local',
                            'vector_facial': '[]',
                            'activo': True,
                            'confianza_enrolamiento': 0.8
                        }
                    )
                    
                    # Actualizar URLs de fotos
                    fotos_actuales = []
                    if reconocimiento.fotos_urls:
                        try:
                            fotos_actuales = json.loads(reconocimiento.fotos_urls)
                            if not isinstance(fotos_actuales, list):
                                fotos_actuales = []
                        except (json.JSONDecodeError, TypeError):
                            fotos_actuales = []
                    
                    # Agregar nuevas URLs
                    fotos_actuales.extend(fotos_urls_subidas)
                    reconocimiento.fotos_urls = json.dumps(fotos_actuales)
                    
                    # Actualizar imagen de referencia si es la primera foto
                    if not reconocimiento.imagen_referencia_url and fotos_urls_subidas:
                        reconocimiento.imagen_referencia_url = fotos_urls_subidas[0]
                    
                    reconocimiento.activo = True
                    reconocimiento.save()
                    
                    print(f"✅ [PANEL PROPIETARIO] Reconocimiento facial actualizado: ID {reconocimiento.id}")
                    print(f"📊 [PANEL PROPIETARIO] Total fotos en sistema: {len(fotos_actuales)}")
                    
                    # 7. Sincronizar con sistema de seguridad
                    try:
                        from seguridad.services.sincronizacion_service import SincronizacionReconocimientoService
                        
                        for foto_url in fotos_urls_subidas:
                            resultado_sync = SincronizacionReconocimientoService.sincronizar_fotos_propietario_a_seguridad(
                                copropietario.id, 
                                foto_url
                            )
                            print(f"🔄 [PANEL PROPIETARIO] Sincronización con seguridad: {resultado_sync.get('success', False)}")
                    except Exception as e:
                        print(f"⚠️ [PANEL PROPIETARIO] Error en sincronización con seguridad: {str(e)}")
                        # No fallar por errores de sincronización
                    
                    # 8. Respuesta exitosa
                    response_data = {
                        'success': True,
                        'message': f'Se procesaron {len(fotos_urls_subidas)} fotos correctamente',
                        'data': {
                            'fotos_subidas': len(fotos_urls_subidas),
                            'total_fotos_sistema': len(fotos_actuales),
                            'reconocimiento_id': reconocimiento.id,
                            'reconocimiento_activo': reconocimiento.activo,
                            'urls_fotos_nuevas': fotos_urls_subidas[:3]  # Mostrar solo las primeras 3 URLs
                        }
                    }
                    
                    if errores_procesamiento:
                        response_data['advertencias'] = errores_procesamiento
                    
                    print(f"🎉 [PANEL PROPIETARIO] Proceso completado exitosamente!")
                    return Response(response_data, status=status.HTTP_200_OK)
                
                else:
                    # No se pudo procesar ninguna foto
                    print("❌ [PANEL PROPIETARIO] No se pudo procesar ninguna foto")
                    return Response({
                        'success': False,
                        'error': 'No se pudo procesar ninguna foto',
                        'detalles': errores_procesamiento
                    }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            error_msg = f"Error interno del servidor: {str(e)}"
            print(f"💥 [PANEL PROPIETARIO] {error_msg}")
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MisFotosDropboxView(APIView):
    """
    Vista mejorada para obtener las fotos del propietario desde Dropbox
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Obtener mis fotos de reconocimiento facial",
        description="Obtiene todas las fotos de reconocimiento facial del propietario autenticado",
        responses={
            200: OpenApiResponse(description="Fotos obtenidas correctamente"),
            404: OpenApiResponse(description="Propietario no encontrado"),
            401: OpenApiResponse(description="No autorizado")
        }
    )
    def get(self, request):
        """Obtener fotos del propietario autenticado"""
        
        print("📸 [PANEL PROPIETARIO] Obteniendo fotos del usuario...")
        
        try:
            usuario = request.user
            
            # Importar modelos
            from seguridad.models import Copropietarios, ReconocimientoFacial
            
            # Buscar copropietario
            try:
                copropietario = Copropietarios.objects.get(usuario_sistema_id=usuario.id)
                print(f"✅ [PANEL PROPIETARIO] Copropietario encontrado: {copropietario.nombres} {copropietario.apellidos}")
            except Copropietarios.DoesNotExist:
                print("❌ [PANEL PROPIETARIO] No se encontró copropietario")
                return Response({
                    'success': False,
                    'error': 'No se encontró información de copropietario para este usuario'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Buscar reconocimiento facial
            try:
                reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
                
                # Obtener URLs de fotos
                fotos_urls = []
                if reconocimiento.fotos_urls:
                    try:
                        fotos_urls = json.loads(reconocimiento.fotos_urls)
                        if not isinstance(fotos_urls, list):
                            fotos_urls = []
                    except (json.JSONDecodeError, TypeError):
                        fotos_urls = []
                
                # Agregar imagen de referencia si existe y no está en la lista
                if reconocimiento.imagen_referencia_url and reconocimiento.imagen_referencia_url not in fotos_urls:
                    fotos_urls.insert(0, reconocimiento.imagen_referencia_url)
                
                response_data = {
                    'success': True,
                    'data': {
                        'total_fotos': len(fotos_urls),
                        'fotos_urls': fotos_urls,
                        'copropietario_id': copropietario.id,
                        'reconocimiento_activo': reconocimiento.activo,
                        'reconocimiento_id': reconocimiento.id,
                        'proveedor_ia': reconocimiento.proveedor_ia,
                        'confianza_enrolamiento': reconocimiento.confianza_enrolamiento
                    }
                }
                
                print(f"📊 [PANEL PROPIETARIO] Fotos encontradas: {len(fotos_urls)}")
                return Response(response_data, status=status.HTTP_200_OK)
                
            except ReconocimientoFacial.DoesNotExist:
                print("📭 [PANEL PROPIETARIO] No hay reconocimiento facial configurado")
                return Response({
                    'success': True,
                    'data': {
                        'total_fotos': 0,
                        'fotos_urls': [],
                        'copropietario_id': copropietario.id,
                        'reconocimiento_activo': False,
                        'reconocimiento_id': None
                    }
                }, status=status.HTTP_200_OK)
        
        except Exception as e:
            error_msg = f"Error interno del servidor: {str(e)}"
            print(f"💥 [PANEL PROPIETARIO] {error_msg}")
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)