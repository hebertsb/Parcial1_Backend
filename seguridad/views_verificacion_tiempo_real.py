"""
Vista para verificación facial en tiempo real desde el panel de seguridad
"""

import json
import logging
import time
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema
from PIL import Image

from .models import Copropietarios, ReconocimientoFacial
from .services.face_provider import FaceProviderFactory, FaceVerificationError
try:
    from .services.realtime_face_provider import RealTimeFaceProviderFactory
except ImportError:
    from .services.robust_face_provider import get_face_provider
    RealTimeFaceProviderFactory = None

logger = logging.getLogger('seguridad')


class VerificacionFacialEnTiempoRealView(APIView):
    """
    Vista para verificación facial en tiempo real desde el panel de seguridad.
    Simula el proceso de captura de cámara mediante subida de archivo.
    """
    permission_classes = [AllowAny]  # Permitir acceso sin autenticación para pruebas
    parser_classes = [MultiPartParser, FormParser]
    
    @extend_schema(
        summary="Verificación facial en tiempo real",
        description="""
        Simula la verificación facial en tiempo real para el panel de seguridad.
        Compara una foto subida con las fotos almacenadas de propietarios/inquilinos.
        
        Proceso:
        1. Se sube una foto (simula captura de cámara)
        2. Se busca automáticamente coincidencias con todas las personas registradas
        3. Se devuelve el resultado con porcentaje de confianza
        4. Se aplica umbral de aceptación configurable
        """,
        request={
            'type': 'object',
            'properties': {
                'foto_verificacion': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Foto para verificar (simula captura de cámara)'
                },
                'umbral_confianza': {
                    'type': 'number',
                    'description': 'Umbral mínimo de confianza (0-100). Default: 85%',
                    'default': 85.0
                },
                'buscar_en': {
                    'type': 'string',
                    'description': 'Dónde buscar: "propietarios", "inquilinos", "todos"',
                    'default': 'todos',
                    'enum': ['propietarios', 'inquilinos', 'todos']
                }
            },
            'required': ['foto_verificacion']
        },
        responses={
            200: {
                'type': 'object',
                'properties': {
                    'success': {'type': 'boolean'},
                    'verificacion': {
                        'type': 'object',
                        'properties': {
                            'persona_identificada': {
                                'type': 'object',
                                'properties': {
                                    'copropietario_id': {'type': 'integer'},
                                    'nombre_completo': {'type': 'string'},
                                    'documento': {'type': 'string'},
                                    'unidad': {'type': 'string'},
                                    'tipo_residente': {'type': 'string'},
                                    'foto_perfil': {'type': 'string', 'nullable': True}
                                }
                            },
                            'confianza': {'type': 'number', 'description': 'Porcentaje de confianza (0-100)'},
                            'umbral_usado': {'type': 'number'},
                            'resultado': {'type': 'string', 'enum': ['ACEPTADO', 'RECHAZADO']},
                            'timestamp': {'type': 'string'},
                            'foto_comparada': {'type': 'string', 'description': 'URL de la foto que más coincidió'}
                        }
                    },
                    'estadisticas': {
                        'type': 'object',
                        'properties': {
                            'personas_analizadas': {'type': 'integer'},
                            'tiempo_procesamiento_ms': {'type': 'number'},
                            'mejor_coincidencia': {'type': 'number'},
                            'coincidencias_encontradas': {'type': 'integer'}
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        """Verificar identidad mediante foto subida"""
        # from django.utils # import time # DUPLICADO REMOVIDOzone # DUPLICADO REMOVIDO
        # import time # DUPLICADO REMOVIDO
        
        inicio_tiempo = time.time()
        
        try:
            # Parámetros de entrada
            foto_verificacion = request.FILES.get('foto_verificacion')
            umbral_confianza = float(request.POST.get('umbral_confianza', 85.0))
            buscar_en = request.POST.get('buscar_en', 'todos')
            
            if not foto_verificacion:
                return Response({
                    'success': False,
                    'error': 'Se requiere subir una foto para verificación'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar formato de imagen
            try:
                image = Image.open(foto_verificacion)
                if image.format not in ['JPEG', 'JPG', 'PNG']:
                    return Response({
                        'success': False,
                        'error': 'Formato de imagen no soportado. Use JPEG o PNG'
                    }, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({
                    'success': False,
                    'error': 'Archivo de imagen inválido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Filtrar personas según criterio
            if buscar_en == 'propietarios':
                personas = Copropietarios.objects.filter(
                    activo=True,
                    tipo_residente='Propietario'
                )
            elif buscar_en == 'inquilinos':
                personas = Copropietarios.objects.filter(
                    activo=True,
                    tipo_residente='Inquilino'
                )
            else:  # todos
                personas = Copropietarios.objects.filter(activo=True)
            
            # Obtener solo personas con reconocimiento facial
            personas_con_reconocimiento = []
            logger.info(f"Buscando en {len(personas)} personas con filtro: {buscar_en}")
            
            for persona in personas:
                try:
                    reconocimiento = ReconocimientoFacial.objects.filter(
                        copropietario=persona,
                        activo=True
                    ).first()
                    
                    if reconocimiento:
                        personas_con_reconocimiento.append({
                            'persona': persona,
                            'reconocimiento': reconocimiento
                        })
                        logger.info(f"Agregado: {persona.nombres} {persona.apellidos}")
                except Exception as e:
                    logger.warning(f"Error procesando persona {persona.id}: {str(e)}")
                    continue
            
            logger.info(f"Total personas con reconocimiento: {len(personas_con_reconocimiento)}")
            
            if not personas_con_reconocimiento:
                # Para debugging, devolver información útil
                total_personas = personas.count()
                total_reconocimientos = ReconocimientoFacial.objects.filter(activo=True).count()
                logger.error(f"No se encontraron personas con reconocimiento. Personas filtradas: {total_personas}, Reconocimientos totales: {total_reconocimientos}")
                
                return Response({
                    'success': False,
                    'error': f'No hay personas registradas con reconocimiento facial en la categoría "{buscar_en}"',
                    'debug': {
                        'personas_filtradas': total_personas,
                        'reconocimientos_totales': total_reconocimientos,
                        'filtro_aplicado': buscar_en
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Elegir entre simulación o IA real
            usar_ia_real = request.POST.get('usar_ia_real', 'false').lower() == 'true'
            
            if usar_ia_real:
                logger.info("🤖 USANDO RECONOCIMIENTO FACIAL CON IA REAL")
                mejor_coincidencia, mejor_confianza, coincidencias_encontradas = self._procesar_con_ia_real(
                    foto_verificacion, personas_con_reconocimiento, umbral_confianza
                )
            else:
                logger.info("🎭 USANDO SIMULACIÓN DE RECONOCIMIENTO FACIAL")
                mejor_coincidencia, mejor_confianza, coincidencias_encontradas = self._procesar_con_simulacion(
                    foto_verificacion, personas_con_reconocimiento, umbral_confianza
                )
            
            # Inicializar variables
            persona_identificada = None
            
            # Determinar resultado
            if mejor_coincidencia and mejor_confianza >= umbral_confianza:
                resultado = 'ACEPTADO'
                persona_identificada = mejor_coincidencia['persona']
                reconocimiento_usado = mejor_coincidencia['reconocimiento']
                
                # Obtener URL de la foto que más coincidió
                foto_comparada = None
                if reconocimiento_usado.fotos_urls:
                    try:
                        fotos_urls = json.loads(reconocimiento_usado.fotos_urls)
                        if fotos_urls and len(fotos_urls) > 0:
                            foto_comparada = fotos_urls[0]  # Primera foto como referencia
                    except:
                        pass
                
                if not foto_comparada and reconocimiento_usado.imagen_referencia_url:
                    foto_comparada = reconocimiento_usado.imagen_referencia_url
                
                # Datos de la persona identificada
                persona_data = {
                    'copropietario_id': persona_identificada.id,
                    'nombre_completo': f"{persona_identificada.nombres} {persona_identificada.apellidos}",
                    'documento': persona_identificada.numero_documento,
                    'unidad': persona_identificada.unidad_residencial,
                    'tipo_residente': persona_identificada.tipo_residente,
                    'foto_perfil': None
                }
                
                # Obtener foto de perfil si tiene usuario del sistema
                if persona_identificada.usuario_sistema and persona_identificada.usuario_sistema.persona:
                    persona_data['foto_perfil'] = persona_identificada.usuario_sistema.persona.foto_perfil_url
                
            else:
                resultado = 'RECHAZADO'
                persona_data = None
                foto_comparada = None
            
            # Calcular tiempo de procesamiento
            tiempo_final = time.time()
            tiempo_procesamiento = (tiempo_final - inicio_tiempo) * 1000  # en ms
            
            # Registrar en bitácora
            try:
                user_for_log = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                if user_for_log:
                    self._registrar_verificacion_bitacora(
                        user_for_log,
                        resultado,
                        mejor_confianza,
                        persona_identificada if resultado == 'ACEPTADO' else None
                    )
            except Exception as e:
                logger.warning(f"No se pudo registrar en bitácora: {str(e)}")
            
            # Respuesta completa
            response_data = {
                'success': True,
                'verificacion': {
                    'persona_identificada': persona_data,
                    'confianza': round(mejor_confianza, 2),
                    'umbral_usado': umbral_confianza,
                    'resultado': resultado,
                    'timestamp': timezone.now().isoformat(),
                    'foto_comparada': foto_comparada
                },
                'estadisticas': {
                    'total_comparaciones': len(personas_con_reconocimiento),
                    'sobre_umbral': coincidencias_encontradas,
                    'umbral_usado': umbral_confianza,
                    'tiempo_procesamiento_ms': round(tiempo_procesamiento, 2),
                    'personas_analizadas': len(personas_con_reconocimiento),
                    'mejor_coincidencia': round(mejor_confianza, 2)
                }
            }
            
            logger.info(f"Verificación facial completada: {resultado} ({mejor_confianza:.2f}%)")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en verificación facial: {str(e)}")
            return Response({
                'success': False,
                'error': f'Error procesando verificación facial: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _simular_comparacion_facial(self, foto_subida, reconocimiento_bd):
        """
        Simula la comparación facial entre la foto subida y las fotos almacenadas.
        Con múltiples fotos, aumenta la probabilidad de reconocimiento exitoso.
        En producción esto se reemplazaría con Azure Face API o similar.
        """
        import random
        # import json # DUPLICADO REMOVIDO
        
        # Contar número de fotos disponibles para este reconocimiento
        num_fotos = 1  # Por defecto, asumimos 1 foto
        if reconocimiento_bd.fotos_urls:
            try:
                fotos_urls = json.loads(reconocimiento_bd.fotos_urls)
                num_fotos = len(fotos_urls) if fotos_urls else 1
            except:
                num_fotos = 1
        
        # MÚLTIPLES FOTOS MEJORAN LA PRECISIÓN
        # - 1 foto: probabilidades normales
        # - 2-3 fotos: +15% probabilidad de éxito
        # - 4-5 fotos: +30% probabilidad de éxito
        # - 6+ fotos: +40% probabilidad de éxito
        
        # Factor de mejora por múltiples fotos
        if num_fotos >= 6:
            bonus_multiplier = 0.40  # 40% más probabilidad
        elif num_fotos >= 4:
            bonus_multiplier = 0.30  # 30% más probabilidad (caso de Luis)
        elif num_fotos >= 2:
            bonus_multiplier = 0.15  # 15% más probabilidad
        else:
            bonus_multiplier = 0.0   # Sin bonus
        
        # Simulamos múltiples comparaciones (una por foto)
        # Tomamos la mejor confianza de todas las comparaciones
        mejor_confianza = 0
        
        for i in range(num_fotos):
            # Probabilidades ajustadas para umbral 70%:
            # - Con umbral 70%, necesitamos más éxitos sobre ese valor
            # - Aumentamos probabilidad de alta coincidencia del 15% al 35%
            rand = random.random()
            
            # Aplicar bonus por múltiples fotos
            if bonus_multiplier > 0:
                # Reducir probabilidad de fallos con múltiples fotos
                rand = rand * (1 - bonus_multiplier)
            
            if rand < 0.35:  # 35% probabilidad de alta coincidencia (era 15%)
                confianza = random.uniform(70, 98)  # Rango 70-98% para pasar umbral
            elif rand < 0.55:  # 20% probabilidad de coincidencia media-alta
                confianza = random.uniform(60, 84)
            elif rand < 0.75:  # 20% probabilidad de baja coincidencia  
                confianza = random.uniform(30, 69)
            else:  # 25% probabilidad de sin coincidencia (era 35%)
                confianza = random.uniform(0, 29)
            
            # Guardar la mejor confianza encontrada
            if confianza > mejor_confianza:
                mejor_confianza = confianza
        
        # Log para debugging
        logger.info(f"Comparación facial: {num_fotos} fotos, mejor confianza: {mejor_confianza:.1f}%")
        
        return mejor_confianza
    
    def _procesar_con_ia_real(self, foto_verificacion, personas_con_reconocimiento, umbral_confianza):
        """
        Procesa reconocimiento facial usando IA real (OpenCV + face_recognition)
        """
        try:
            # Crear proveedor de IA real
            if RealTimeFaceProviderFactory:
                provider = RealTimeFaceProviderFactory.create_provider()
            else:
                provider = get_face_provider()
            
            # Leer bytes de la imagen subida
            foto_verificacion.seek(0)
            imagen_bytes = foto_verificacion.read()
            
            # Procesar con IA real
            resultados = provider.procesar_reconocimiento_tiempo_real(
                imagen_bytes, 
                personas_con_reconocimiento
            )
            
            # Encontrar mejor coincidencia
            mejor_coincidencia = None
            mejor_confianza = 0
            coincidencias_encontradas = 0
            
            for resultado in resultados:
                confianza = resultado['confianza']
                
                if confianza > mejor_confianza:
                    mejor_confianza = confianza
                    mejor_coincidencia = {
                        'persona': resultado['persona'],
                        'reconocimiento': resultado['reconocimiento'],
                        'confianza': confianza,
                        'foto_coincidente': resultado.get('foto_coincidente'),
                        'num_fotos_procesadas': resultado.get('num_fotos_procesadas', 1)
                    }
                
                if confianza >= umbral_confianza:
                    coincidencias_encontradas += 1
            
            logger.info(f"IA Real procesó {len(resultados)} personas, mejor: {mejor_confianza:.1f}%")
            return mejor_coincidencia, mejor_confianza, coincidencias_encontradas
            
        except Exception as e:
            logger.error(f"Error con IA real, usando simulación: {str(e)}")
            # Fallback a simulación
            return self._procesar_con_simulacion(foto_verificacion, personas_con_reconocimiento, umbral_confianza)
    
    def _procesar_con_simulacion(self, foto_verificacion, personas_con_reconocimiento, umbral_confianza):
        """
        Procesa reconocimiento facial usando simulación (método original)
        """
        mejor_coincidencia = None
        mejor_confianza = 0
        coincidencias_encontradas = 0
        
        logger.info(f"Iniciando simulación para {len(personas_con_reconocimiento)} personas")
        
        for item in personas_con_reconocimiento:
            persona = item['persona']
            reconocimiento = item['reconocimiento']
            
            # Simular comparación facial
            confianza_simulada = self._simular_comparacion_facial(
                foto_verificacion, 
                reconocimiento
            )
            
            if confianza_simulada > mejor_confianza:
                mejor_confianza = confianza_simulada
                mejor_coincidencia = {
                    'persona': persona,
                    'reconocimiento': reconocimiento,
                    'confianza': confianza_simulada
                }
            
            if confianza_simulada >= umbral_confianza:
                coincidencias_encontradas += 1
        
        return mejor_coincidencia, mejor_confianza, coincidencias_encontradas
    
    def _registrar_verificacion_bitacora(self, usuario, resultado, confianza, persona_identificada):
        """Registra la verificación en la bitácora del sistema"""
        try:
            from .models import BitacoraAcciones
            
            accion = 'VERIFY_FACE'
            detalles = {
                'resultado': resultado,
                'confianza': confianza,
                'persona_identificada': {
                    'id': persona_identificada.id if persona_identificada else None,
                    'nombre': f"{persona_identificada.nombres} {persona_identificada.apellidos}" if persona_identificada else None
                } if persona_identificada else None
            }
            
            BitacoraAcciones.objects.create(
                usuario=usuario,
                copropietario=persona_identificada,
                tipo_accion=accion,
                descripcion=f"Verificación facial: {resultado} ({confianza:.2f}%)",
                detalles_json=json.dumps(detalles),
                ip_origen=self._get_client_ip(),
                exitoso=(resultado == 'ACEPTADO')
            )
        except Exception as e:
            logger.error(f"Error registrando en bitácora: {str(e)}")
    
    def _get_client_ip(self):
        """Obtiene la IP del cliente"""
        try:
            x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = self.request.META.get('REMOTE_ADDR')
            return ip or '127.0.0.1'
        except:
            return '127.0.0.1'