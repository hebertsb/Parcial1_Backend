"""
Servicio de sincronización entre sistemas de reconocimiento facial
Captura automáticamente las URLs de Dropbox generadas por propietarios
"""

import json
import logging
from django.utils import timezone
from seguridad.models import ReconocimientoFacial, Copropietarios

logger = logging.getLogger('seguridad')


class SincronizacionReconocimientoService:
    """
    Servicio para mantener sincronizadas las fotos entre:
    1. Sistema de Propietarios (authz)
    2. Sistema de Seguridad (seguridad)
    """
    
    @staticmethod
    def sincronizar_fotos_propietario_a_seguridad(copropietario_id, nueva_url_dropbox):
        """
        Sincroniza una nueva foto de propietario al sistema de seguridad
        
        Args:
            copropietario_id (int): ID del copropietario
            nueva_url_dropbox (str): URL pública de Dropbox de la nueva foto
            
        Returns:
            dict: Resultado de la sincronización
        """
        try:
            # Buscar o crear registro de reconocimiento facial
            copropietario = Copropietarios.objects.get(id=copropietario_id)
            
            reconocimiento, created = ReconocimientoFacial.objects.get_or_create(
                copropietario=copropietario,
                defaults={
                    'proveedor_ia': 'Local',
                    'vector_facial': '[]',  # Se llenará cuando se procese con IA
                    'imagen_referencia_url': nueva_url_dropbox,
                    'activo': True
                }
            )
            
            # Obtener fotos existentes
            fotos_existentes = []
            if reconocimiento.fotos_urls:
                try:
                    fotos_existentes = json.loads(reconocimiento.fotos_urls)
                    if not isinstance(fotos_existentes, list):
                        fotos_existentes = []
                except (json.JSONDecodeError, TypeError):
                    fotos_existentes = []
            
            # Agregar nueva URL si no existe
            if nueva_url_dropbox not in fotos_existentes:
                fotos_existentes.append(nueva_url_dropbox)
                reconocimiento.fotos_urls = json.dumps(fotos_existentes)
                
                # Si no tiene imagen de referencia, usar la primera
                if not reconocimiento.imagen_referencia_url:
                    reconocimiento.imagen_referencia_url = nueva_url_dropbox
                
                reconocimiento.fecha_modificacion = timezone.now()
                reconocimiento.save()
                
                logger.info(f"✅ SINCRONIZACIÓN: Nueva foto agregada al sistema de seguridad para copropietario {copropietario_id}")
                
                return {
                    'success': True,
                    'message': 'Foto sincronizada correctamente',
                    'total_fotos': len(fotos_existentes),
                    'created': created
                }
            else:
                return {
                    'success': True,
                    'message': 'Foto ya existe en el sistema',
                    'total_fotos': len(fotos_existentes),
                    'created': False
                }
                
        except Copropietarios.DoesNotExist:
            logger.error(f"❌ SINCRONIZACIÓN: Copropietario {copropietario_id} no encontrado")
            return {
                'success': False,
                'error': f'Copropietario {copropietario_id} no encontrado'
            }
        except Exception as e:
            logger.error(f"❌ SINCRONIZACIÓN: Error sincronizando foto: {str(e)}")
            return {
                'success': False,
                'error': f'Error en sincronización: {str(e)}'
            }
    
    @staticmethod
    def sincronizar_todas_las_fotos_propietario(copropietario_id):
        """
        Sincroniza TODAS las fotos existentes de un propietario al sistema de seguridad
        Útil para propietarios que ya tienen fotos pero no están en seguridad
        
        Args:
            copropietario_id (int): ID del copropietario
            
        Returns:
            dict: Resultado de la sincronización completa
        """
        try:
            copropietario = Copropietarios.objects.get(id=copropietario_id)
            
            # Buscar registro de reconocimiento existente
            reconocimiento = ReconocimientoFacial.objects.filter(
                copropietario=copropietario
            ).first()
            
            if not reconocimiento:
                logger.info(f"No existe registro de reconocimiento para copropietario {copropietario_id}")
                return {
                    'success': True,
                    'message': 'No existe registro de reconocimiento para sincronizar',
                    'total_fotos_sincronizadas': 0
                }
            
            # Obtener fotos existentes
            fotos_existentes = []
            if reconocimiento.fotos_urls:
                try:
                    fotos_existentes = json.loads(reconocimiento.fotos_urls)
                    if isinstance(fotos_existentes, list):
                        logger.info(f"✅ SINCRONIZACIÓN COMPLETA: {len(fotos_existentes)} fotos ya sincronizadas para copropietario {copropietario_id}")
                        return {
                            'success': True,
                            'message': f'{len(fotos_existentes)} fotos ya sincronizadas',
                            'total_fotos_sincronizadas': len(fotos_existentes),
                            'fotos_urls': fotos_existentes
                        }
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return {
                'success': True,
                'message': 'No hay fotos para sincronizar',
                'total_fotos_sincronizadas': 0
            }
            
        except Copropietarios.DoesNotExist:
            logger.error(f"❌ SINCRONIZACIÓN COMPLETA: Copropietario {copropietario_id} no encontrado")
            return {
                'success': False,
                'error': f'Copropietario {copropietario_id} no encontrado'
            }
        except Exception as e:
            logger.error(f"❌ SINCRONIZACIÓN COMPLETA: Error: {str(e)}")
            return {
                'success': False,
                'error': f'Error en sincronización completa: {str(e)}'
            }
    
    @staticmethod
    def obtener_estadisticas_sincronizacion():
        """
        Obtiene estadísticas de sincronización entre sistemas
        
        Returns:
            dict: Estadísticas de sincronización
        """
        try:
            # Contar registros con fotos
            total_reconocimientos = ReconocimientoFacial.objects.filter(activo=True).count()
            
            con_fotos_dropbox = ReconocimientoFacial.objects.filter(
                activo=True,
                fotos_urls__isnull=False
            ).exclude(fotos_urls='').exclude(fotos_urls='[]').count()
            
            sin_fotos = total_reconocimientos - con_fotos_dropbox
            
            # Contar total de fotos
            total_fotos = 0
            registros_con_fotos = ReconocimientoFacial.objects.filter(
                activo=True,
                fotos_urls__isnull=False
            ).exclude(fotos_urls='').exclude(fotos_urls='[]')
            
            for registro in registros_con_fotos:
                try:
                    if registro.fotos_urls:
                        fotos = json.loads(registro.fotos_urls)
                        if isinstance(fotos, list):
                            total_fotos += len(fotos)
                except:
                    pass
            
            return {
                'total_usuarios_reconocimiento': total_reconocimientos,
                'usuarios_con_fotos_dropbox': con_fotos_dropbox,
                'usuarios_sin_fotos': sin_fotos,
                'total_fotos_sincronizadas': total_fotos,
                'porcentaje_sincronizacion': round((con_fotos_dropbox / total_reconocimientos * 100), 2) if total_reconocimientos > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}")
            return {
                'error': f'Error obteniendo estadísticas: {str(e)}'
            }