# RECONOCIMIENTO FACIAL - ADAPTADO A MODELOS EXISTENTES
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
import json
import base64
import io
import numpy as np
from PIL import Image
from datetime import datetime
from django.utils import timezone

# Lazy import de face_recognition para evitar errores al arrancar Django
def get_face_recognition():
    try:
        import face_recognition
        return face_recognition
    except ImportError as e:
        raise ImportError(
            "face_recognition no está disponible. "
            "Instala con: pip install face_recognition"
        ) from e

# Importar modelos existentes
from authz.models import Usuario, Persona
from seguridad.models import Copropietarios, ReconocimientoFacial
from core.models import Vivienda

class FacialRecognitionService:
    """Servicio para reconocimiento facial usando modelos existentes"""
    
    @staticmethod
    def convertir_imagen_base64_a_encoding(imagen_base64):
        """Convertir imagen base64 a encoding facial"""
        try:
            # Limpiar el string base64
            if 'data:image' in imagen_base64:
                imagen_base64 = imagen_base64.split(',')[1]
            
            # Decodificar base64
            imagen_bytes = base64.b64decode(imagen_base64)
            imagen = Image.open(io.BytesIO(imagen_bytes))
            
            # Convertir a RGB si es necesario
            if imagen.mode != 'RGB':
                imagen = imagen.convert('RGB')
            
            # Convertir a numpy array
            imagen_np = np.array(imagen)
            
            # Generar encoding facial
            face_recognition = get_face_recognition()
            face_encodings = face_recognition.face_encodings(imagen_np)
            
            if face_encodings:
                return json.dumps(face_encodings[0].tolist())
            else:
                return None
                
        except Exception as e:
            print(f"Error procesando imagen: {e}")
            return None
    
    @staticmethod
    def comparar_encodings(encoding_actual, encoding_almacenado):
        """Comparar dos encodings faciales"""
        try:
            face_recognition = get_face_recognition()
            encoding_db = np.array(json.loads(encoding_almacenado))
            encoding_act = np.array(json.loads(encoding_actual))
            
            # Comparar rostros con tolerancia
            resultados = face_recognition.compare_faces(
                [encoding_db], encoding_act, tolerance=0.6
            )
            
            # Calcular distancia y confianza
            distancias = face_recognition.face_distance([encoding_db], encoding_act)
            confianza = (1 - distancias[0]) * 100
            
            return resultados[0], round(confianza, 2)
            
        except Exception as e:
            print(f"Error comparando encodings: {e}")
            return False, 0.0

# API ENDPOINTS PARA RECONOCIMIENTO FACIAL

@csrf_exempt
@require_http_methods(["POST"])
def reconocimiento_facial_simulado(request):
    """
    Endpoint principal para reconocimiento facial simulado
    Recibe imagen cargada por el usuario como si fuera de la cámara
    """
    try:
        data = json.loads(request.body)
        imagen_base64 = data.get('imagen')
        
        if not imagen_base64:
            return JsonResponse({'error': 'No se proporcionó imagen'}, status=400)
        
        # Convertir imagen a encoding
        encoding_actual = FacialRecognitionService.convertir_imagen_base64_a_encoding(imagen_base64)
        
        if not encoding_actual:
            return JsonResponse({
                'reconocido': False,
                'error': 'No se detectó rostro en la imagen',
                'mensaje': 'Por favor, asegúrese de que la imagen contenga un rostro visible'
            })
        
        # Buscar en usuarios con reconocimiento facial activo
        usuarios_activos = ReconocimientoFacial.objects.filter(
            activo=True
        ).exclude(
            vector_facial__isnull=True
        ).exclude(
            vector_facial=''
        ).select_related('copropietario')
        
        mejor_coincidencia = None
        mejor_confianza = 0
        
            # Comparar con cada usuario registrado
        for registro_facial in usuarios_activos:
            coincide, confianza = FacialRecognitionService.comparar_encodings(
                encoding_actual, registro_facial.vector_facial
            )            # Umbral de confianza mínimo del 70%
            if coincide and confianza > 70 and confianza > mejor_confianza:
                mejor_coincidencia = registro_facial
                mejor_confianza = confianza
        
        if mejor_coincidencia:
            # Solo maneja copropietarios por ahora (el modelo actual solo tiene copropietario)
            persona_data = {
                'id': mejor_coincidencia.copropietario.id,
                'nombre': mejor_coincidencia.copropietario.nombres,
                'apellido': mejor_coincidencia.copropietario.apellidos,
                'numero_casa': mejor_coincidencia.copropietario.unidad_residencial,
                'tipo': mejor_coincidencia.copropietario.tipo_residente,
                'documento': mejor_coincidencia.copropietario.numero_documento,
                'telefono': mejor_coincidencia.copropietario.telefono or '',
                # Foto desde imagen_referencia_url
                'foto_perfil': mejor_coincidencia.imagen_referencia_url or '/static/img/default-avatar.png'
            }
            
            # Registrar acceso exitoso
            registro_acceso = {
                'usuario_reconocido': mejor_coincidencia,
                'confianza': mejor_confianza,
                'fecha_acceso': timezone.now(),
                'tipo_acceso': 'RECONOCIMIENTO_FACIAL_SIMULADO',
                'exitoso': True
            }
            
            # Aquí podrías guardar en un modelo de RegistroAcceso si lo creas
            # O simplemente log el acceso
            
            return JsonResponse({
                'reconocido': True,
                'confianza': mejor_confianza,
                'persona': persona_data,
                'mensaje': f'Acceso permitido para {persona_data["nombre"]} {persona_data["apellido"]}',
                'hora_acceso': timezone.now().strftime('%H:%M:%S'),
                'fecha_acceso': timezone.now().strftime('%d/%m/%Y')
            })
        
        else:
            # No se encontró coincidencia
            return JsonResponse({
                'reconocido': False,
                'mensaje': 'Persona no reconocida en el sistema',
                'sugerencia': 'Verificar manualmente o contactar administración',
                'confianza': 0
            })
            
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Formato JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error interno: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lista_usuarios_reconocimiento(request):
    """
    Lista de todos los usuarios con reconocimiento facial activo
    Para uso del panel del guardia
    """
    try:
        usuarios_activos = ReconocimientoFacial.objects.filter(
            activo=True
        ).select_related('copropietario')
        
        lista_usuarios = []
        
        for registro in usuarios_activos:
            # Solo maneja copropietarios (el modelo actual no tiene campo inquilino)
            usuario_data = {
                'id': registro.copropietario.id,
                'nombre': registro.copropietario.nombres,
                'apellido': registro.copropietario.apellidos,
                'documento_identidad': registro.copropietario.numero_documento,
                'numero_casa': registro.copropietario.unidad_residencial,
                'telefono': registro.copropietario.telefono or '',
                'email': registro.copropietario.email or '',
                'tipo_residente': registro.copropietario.tipo_residente,
                # Usar imagen_referencia_url como foto de perfil
                'foto_perfil': registro.imagen_referencia_url or '/static/img/default-avatar.png',
                'reconocimiento_facial_activo': registro.activo,
                'fecha_registro': registro.fecha_enrolamiento.strftime('%d/%m/%Y'),
                'tipo_usuario': 'Copropietario'
            }
            
            lista_usuarios.append(usuario_data)
        
        # Ordenar por nombre
        lista_usuarios.sort(key=lambda x: f"{x['nombre']} {x['apellido']}")
        
        return Response({
            'usuarios': lista_usuarios,
            'total': len(lista_usuarios),
            'activos': len([u for u in lista_usuarios if u['reconocimiento_facial_activo']]),
            'timestamp': timezone.now().isoformat()
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error obteniendo lista de usuarios: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def buscar_usuarios_reconocimiento(request):
    """Buscar usuarios por nombre, documento o casa"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query:
            return Response({'usuarios': [], 'mensaje': 'Proporcione un término de búsqueda'})
        
        # Buscar en copropietarios con reconocimiento facial activo
        registros_encontrados = ReconocimientoFacial.objects.filter(
            activo=True
        ).filter(
            Q(copropietario__nombres__icontains=query) |
            Q(copropietario__apellidos__icontains=query) |
            Q(copropietario__numero_documento__icontains=query) |
            Q(copropietario__unidad_residencial__icontains=query)
        ).select_related('copropietario')
        
        resultados = []
        
        # Procesar resultados encontrados
        for registro in registros_encontrados:
            coprop = registro.copropietario
            resultados.append({
                'id': coprop.id,
                'nombre': coprop.nombres,
                'apellido': coprop.apellidos,
                'documento_identidad': coprop.numero_documento,
                'numero_casa': coprop.unidad_residencial,
                'telefono': coprop.telefono or '',
                'foto_perfil': registro.imagen_referencia_url or '/static/img/default-avatar.png',
                'tipo_usuario': 'Copropietario'
            })
        
        return Response({
            'usuarios': resultados,
            'total_encontrados': len(resultados),
            'termino_busqueda': query
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error en búsqueda: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def estadisticas_reconocimiento(request):
    """Estadísticas para el dashboard del guardia"""
    try:
        # Contar usuarios activos (solo copropietarios por ahora)
        total_activos = ReconocimientoFacial.objects.filter(activo=True).count()
        copropietarios_activos = total_activos  # Todos son copropietarios
        inquilinos_activos = 0  # Sin soporte aún
        
        # Últimos registros
        ultimos_registros = ReconocimientoFacial.objects.filter(
            activo=True
        ).select_related('copropietario').order_by('-fecha_modificacion')[:5]
        
        ultimos_data = []
        for registro in ultimos_registros:
            coprop = registro.copropietario
            ultimos_data.append({
                'nombre': f"{coprop.nombres} {coprop.apellidos}",
                'casa': coprop.unidad_residencial,
                'tipo': coprop.tipo_residente,
                'fecha': registro.fecha_modificacion.strftime('%d/%m/%Y %H:%M')
            })
        
        return Response({
            'total_usuarios_activos': total_activos,
            'copropietarios_activos': copropietarios_activos,
            'inquilinos_activos': inquilinos_activos,
            'ultimos_registros': ultimos_data,
            'fecha_consulta': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Exception as e:
        return Response(
            {'error': f'Error obteniendo estadísticas: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )