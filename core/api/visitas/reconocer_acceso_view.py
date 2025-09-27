import face_recognition
import numpy as np
import logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s %(message)s')
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from core.api.visitas.acceso_facial_serializer import AccesoFacialSerializer
from core.models.propiedades_residentes import Visita
from authz.models import Persona

class ReconocerAccesoVisitaAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        print("[DEBUG] Usuario autenticado:", getattr(request.user, 'email', str(request.user)))
        serializer = AccesoFacialSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        imagen_acceso = serializer.validated_data['imagen_acceso']
        try:
            # Codificar rostro de la imagen recibida
            img = face_recognition.load_image_file(imagen_acceso)
            encodings = face_recognition.face_encodings(img)
            if not encodings:
                return Response({'detail': 'No se detectó ningún rostro en la imagen.'}, status=400)
            encoding_acceso = encodings[0]
            print("[DEBUG] Se detectó rostro en imagen de acceso.")
        except Exception as e:
            return Response({'detail': f'Error procesando la imagen: {str(e)}'}, status=400)

        # Buscar visitas programadas o en curso
        visitas = Visita.objects.filter(estado__in=['programada', 'en_curso'])
        print(f"[DEBUG] Visitas a evaluar: {[v.id for v in visitas]}")
        from core.utils.download_image import download_image_from_url
        mejor_distancia = 1.0
        visita_match = None
        nombre_visitante_match = None
        for visita in visitas:
            print(f"[DEBUG] Evaluando visita {visita.id} - {visita.nombre_visitante}")
            urls = visita.fotos_reconocimiento or []
            encodings_db = []
            for url in urls:
                try:
                    img_file = download_image_from_url(url)
                    print(f"[DEBUG] Descargada imagen de Dropbox: {url}")
                    img = face_recognition.load_image_file(img_file)
                    encs = face_recognition.face_encodings(img)
                    if encs:
                        print(f"[DEBUG] Se detectó rostro en imagen: {url}")
                        encodings_db.append(encs[0])
                    else:
                        print(f"[DEBUG] No se detectó rostro en imagen: {url}")
                except Exception as e:
                    print(f"[DEBUG] Error al procesar imagen {url}: {e}")
                    continue
            if not encodings_db:
                print(f"[DEBUG] Ningún encoding facial válido para visita {visita.id}")
                continue
            encodings_db_np = np.array(encodings_db)
            if len(encodings_db_np.shape) == 1:
                encodings_db_np = np.expand_dims(encodings_db_np, axis=0)
            distancias = face_recognition.face_distance(encodings_db_np, encoding_acceso)
            print(f"[DEBUG] Distancias para visita {visita.id}: {distancias}")
            distancia_min = np.min(distancias)
            # Usar un umbral estricto para coincidencia facial
            print(f"[DEBUG] Menor distancia para visita {visita.id}: {distancia_min}")
            if distancia_min < 0.60 and distancia_min < mejor_distancia:
                print(f"[DEBUG] ¡Coincidencia candidata! (distancia={distancia_min}) para visita {visita.id}")
                mejor_distancia = distancia_min
                visita_match = visita
        if not visita_match:
            print("[DEBUG] No se encontró coincidencia facial suficiente.")
            return Response({'autorizado': False, 'detail': 'No se encontró coincidencia facial.'}, status=403)

        ahora = timezone.now()
        if visita_match.estado == 'programada':
            print(f"[DEBUG] Acceso autorizado para visita {visita_match.id} ({visita_match.nombre_visitante})")
            visita_match.fecha_hora_llegada = ahora
            visita_match.estado = 'en_curso'
            visita_match.save()
            return Response({'autorizado': True, 'nombre': visita_match.nombre_visitante, 'estado': 'en_curso', 'detail': 'Acceso autorizado. Visitante ingresando.'})
        elif visita_match.estado == 'en_curso':
            print(f"[DEBUG] Salida registrada para visita {visita_match.id} ({visita_match.nombre_visitante})")
            visita_match.fecha_hora_salida = ahora
            visita_match.estado = 'finalizada'
            visita_match.save()
            return Response({'autorizado': True, 'nombre': visita_match.nombre_visitante, 'estado': 'finalizada', 'detail': 'Salida registrada. Visitante saliendo.'})
        else:
            print(f"[DEBUG] Estado de visita no permite acceso: {visita_match.estado}")
            return Response({'autorizado': False, 'detail': 'El estado de la visita no permite registrar acceso.'}, status=400)
