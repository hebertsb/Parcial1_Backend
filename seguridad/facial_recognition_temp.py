# Versión temporal del servicio de reconocimiento facial para debugging
import json
import base64
import io
import numpy as np
from PIL import Image
from django.utils import timezone

# Importar modelos existentes
from authz.models import Persona
from seguridad.models import Copropietarios

class FacialRecognitionService:
    """Servicio para reconocimiento facial usando modelos existentes - Versión temporal sin face_recognition"""
    
    @staticmethod
    def procesar_imagen_base64(imagen_base64):
        """Procesar imagen base64 y generar encoding facial - VERSIÓN SIMULADA"""
        try:
            # Decodificar imagen base64
            imagen_bytes = base64.b64decode(imagen_base64)
            imagen = Image.open(io.BytesIO(imagen_bytes))
            
            # Simular encoding facial con datos aleatorios pero consistentes
            # En un entorno real, aquí usaríamos face_recognition
            np.random.seed(42)  # Seed fijo para consistencia
            fake_encoding = np.random.rand(128).tolist()
            
            return json.dumps(fake_encoding)
                
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None
    
    @staticmethod
    def comparar_encodings(encoding_actual, encoding_almacenado):
        """Comparar dos encodings faciales - VERSIÓN SIMULADA"""
        try:
            # Simular comparación exitosa para fines de testing
            return True, 85.5  # Siempre retorna match con 85.5% de confianza
            
        except Exception as e:
            print(f"Error comparando encodings: {e}")
            return False, 0.0
    
    @staticmethod
    def reconocimiento_facial_simulado(imagen_base64):
        """
        Reconocimiento facial completo - VERSIÓN SIMULADA
        Retorna los mismos usuarios de prueba que creamos anteriormente
        """
        try:
            # Simular que siempre encuentra a Juan Carlos Mendoza (primer usuario)
            copropietario = Copropietarios.objects.filter(
                reconocimiento_facial__activo=True
            ).first()
            
            if copropietario:
                reconocimiento = getattr(copropietario, 'reconocimiento_facial', None)
                
                return {
                    'reconocido': True,
                    'persona': {
                        'id': copropietario.id,
                        'nombre': copropietario.nombres,
                        'apellido': copropietario.apellidos,
                        'documento': copropietario.numero_documento,
                        'numero_casa': copropietario.unidad_residencial,
                        'telefono': copropietario.telefono or 'No disponible',
                        'email': copropietario.email or 'No disponible',
                        'tipo': copropietario.tipo_residente,
                        'foto_perfil': reconocimiento.imagen_referencia_url if reconocimiento else None
                    },
                    'confianza': 85.5,
                    'mensaje': 'Reconocimiento exitoso - Acceso autorizado',
                    'hora_acceso': timezone.now().strftime('%H:%M:%S'),
                    'fecha_acceso': timezone.now().strftime('%d/%m/%Y')
                }
            else:
                return {
                    'reconocido': False,
                    'persona': None,
                    'confianza': 0.0,
                    'mensaje': 'No se pudo identificar a la persona',
                    'hora_acceso': timezone.now().strftime('%H:%M:%S'),
                    'fecha_acceso': timezone.now().strftime('%d/%m/%Y')
                }
                
        except Exception as e:
            print(f"Error en reconocimiento facial: {e}")
            return {
                'reconocido': False,
                'persona': None,
                'confianza': 0.0,
                'mensaje': f'Error en el sistema: {str(e)}',
                'hora_acceso': timezone.now().strftime('%H:%M:%S'),
                'fecha_acceso': timezone.now().strftime('%d/%m/%Y')
            }
    
    @staticmethod
    def obtener_usuarios_activos():
        """Obtener lista de usuarios con reconocimiento facial activo"""
        try:
            copropietarios = Copropietarios.objects.filter(
                reconocimiento_facial__activo=True
            ).distinct()
            
            usuarios = []
            for copropietario in copropietarios:
                reconocimiento = getattr(copropietario, 'reconocimiento_facial', None)
                
                usuarios.append({
                    'id': copropietario.id,
                    'nombre': copropietario.nombres,
                    'apellido': copropietario.apellidos,
                    'documento_identidad': copropietario.numero_documento,
                    'numero_casa': copropietario.unidad_residencial,
                    'telefono': copropietario.telefono or 'No disponible',
                    'email': copropietario.email or 'No disponible',
                    'tipo_residente': copropietario.tipo_residente,
                    'foto_perfil': reconocimiento.imagen_referencia_url if reconocimiento else None,
                    'reconocimiento_facial_activo': True,
                    'fecha_registro': reconocimiento.fecha_enrolamiento.strftime('%d/%m/%Y') if reconocimiento else 'N/A',
                    'tipo_usuario': 'Copropietario'
                })
            
            return usuarios
            
        except Exception as e:
            print(f"Error obteniendo usuarios activos: {e}")
            return []
    
    @staticmethod
    def buscar_usuarios(termino_busqueda):
        """Buscar usuarios por término de búsqueda"""
        try:
            usuarios = FacialRecognitionService.obtener_usuarios_activos()
            
            if not termino_busqueda:
                return usuarios
            
            # Filtrar usuarios según el término de búsqueda
            usuarios_filtrados = []
            termino = termino_busqueda.lower()
            
            for usuario in usuarios:
                if (termino in usuario['nombre'].lower() or
                    termino in usuario['apellido'].lower() or
                    termino in str(usuario['documento_identidad']) or
                    termino in str(usuario['numero_casa']).lower()):
                    usuarios_filtrados.append(usuario)
            
            return usuarios_filtrados
            
        except Exception as e:
            print(f"Error buscando usuarios: {e}")
            return []
    
    @staticmethod
    def obtener_estadisticas():
        """Obtener estadísticas del sistema"""
        try:
            total_usuarios = Copropietarios.objects.count()
            usuarios_activos = Copropietarios.objects.filter(
                reconocimiento_facial__activo=True
            ).distinct().count()
            usuarios_inactivos = total_usuarios - usuarios_activos
            
            # Estadísticas simuladas para la demo
            return {
                'total_usuarios': total_usuarios,
                'usuarios_activos': usuarios_activos,
                'usuarios_inactivos': usuarios_inactivos,
                'reconocimientos_hoy': 12,  # Simulado
                'accesos_exitosos': 10,      # Simulado
                'accesos_fallidos': 2,       # Simulado
                'ultima_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }
            
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {
                'total_usuarios': 0,
                'usuarios_activos': 0,
                'usuarios_inactivos': 0,
                'reconocimientos_hoy': 0,
                'accesos_exitosos': 0,
                'accesos_fallidos': 0,
                'ultima_actualizacion': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }