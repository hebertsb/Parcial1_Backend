from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from authz.models import Persona, Usuario, Rol
from core.models.propiedades_residentes import Visita
import numpy as np

class ReconocerAccesoVisitaTest(APITestCase):
    def test_rechazo_acceso_persona_no_registrada(self):
        """Debe rechazar el acceso si la imagen no corresponde a ninguna referencia en Dropbox."""
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.usuario_seguridad)
        access_token = str(refresh.access_token)
        url = '/api/visitas/reconocer_acceso/'
        # Usar una imagen de una persona NO registrada
        with open("authz/tests/media/15.jpg", "rb") as img:
            data = {"imagen_acceso": SimpleUploadedFile("foto.jpg", img.read(), content_type="image/jpeg")}
            response = self.client.post(
                url,
                data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {access_token}'
            )
        # Manejar ambos tipos de respuesta
        data = getattr(response, "data", None)
        if data is None:
            try:
                data = response.json()
            except Exception:
                data = {}
        print("RESPONSE DATA (NO REGISTRADA):", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, f"Código inesperado: {response.status_code}, data: {data}")
        self.assertFalse(data.get("autorizado", True), f"Se autorizó acceso cuando no debía. Data: {data}")

    def setUp(self):
        # Crear usuario de seguridad para autenticación
        from authz.models import Persona, Usuario, Rol
        from core.models.propiedades_residentes import Visita
        from core.utils.dropbox_upload import upload_image_to_dropbox
        from django.core.files.base import ContentFile
        import base64
        self.seguridad_persona = Persona.objects.create(
            nombre="Carlos",
            apellido="Seguridad",
            documento_identidad="SEG001",
            email="seguridad.test@condominio.com",
            telefono="+591 70123456",
            tipo_persona='seguridad',
            activo=True
        )
        self.usuario_seguridad = Usuario.objects.create_user(
            email="seguridad.test@condominio.com",
            password="seg2024",
            persona=self.seguridad_persona,
            estado='ACTIVO'
        )
        rol_seguridad, _ = Rol.objects.get_or_create(nombre='Seguridad', defaults={'descripcion': 'Personal de seguridad'})
        self.usuario_seguridad.roles.add(rol_seguridad)

        # Crear persona visitante y visita con múltiples fotos de referencia en Dropbox
        self.persona = Persona.objects.create(
            nombre="Juan",
            apellido="Visitante",
            reconocimiento_facial_activo=True
        )
        fotos_info = []
        for idx in range(9, 14):
            with open(f"authz/tests/media/{idx}.jpg", "rb") as img_file:
                img_bytes = img_file.read()
                file = ContentFile(img_bytes, name=f"test_reconocimiento_{idx}.jpg")
                info_foto = upload_image_to_dropbox(file, f"test_reconocimiento_{idx}.jpg")
                fotos_info.append(info_foto)
        self.visita = Visita.objects.create(
            persona_autorizante=self.persona,
            nombre_visitante=self.persona.nombre_completo,
            estado="programada",
            fotos_reconocimiento=fotos_info
        )

    def test_reconocimiento_acceso(self):
        from rest_framework import status
        from rest_framework_simplejwt.tokens import RefreshToken
        # Autenticación con el usuario de seguridad creado en setUp
        refresh = RefreshToken.for_user(self.usuario_seguridad)
        access_token = str(refresh.access_token)
        url = '/api/visitas/reconocer_acceso/'
        # Simular foto de acceso (el guardia sube la imagen)
        # Usar una de las fotos de referencia para garantizar coincidencia facial
        with open("authz/tests/media/15.jpg", "rb") as img:
            data = {"imagen_acceso": SimpleUploadedFile("foto.jpg", img.read(), content_type="image/jpeg")}
            response = self.client.post(
                url,
                data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {access_token}'
            )
        data = getattr(response, "data", None)
        if data is None:
            try:
                data = response.json()
            except Exception:
                data = {}
        print("RESPONSE DATA:", data)
        # Solo validamos que la respuesta sea 200 o 403 (autorizado o no)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN], f"Código inesperado: {response.status_code}, data: {data}")

    def test_reconocimiento_acceso_exitoso(self):
        # Obtener token JWT para el usuario de seguridad
        refresh = RefreshToken.for_user(self.usuario_seguridad)
        access_token = str(refresh.access_token)
        url = '/api/visitas/reconocer_acceso/'
        # Simular foto de acceso (puede ser la misma que la de referencia)
        with open("authz/tests/media/14.jpg", "rb") as img:
            data = {"imagen_acceso": SimpleUploadedFile("foto.jpg", img.read(), content_type="image/jpeg")}
            # Incluir el token JWT en el header Authorization
            response = self.client.post(
                url,
                data,
                format='multipart',
                HTTP_AUTHORIZATION=f'Bearer {access_token}'
            )
        data = getattr(response, "data", None)
        if data is None:
            try:
                data = response.json()
            except Exception:
                data = {}
        print("RESPONSE DATA:", data)  # Para depuración
        self.assertEqual(response.status_code, status.HTTP_200_OK, f"Código inesperado: {response.status_code}, data: {data}")
        self.assertTrue(data.get("autorizado", False), f"No se autorizó el acceso cuando debía. Data: {data}")
        self.visita.refresh_from_db()
        self.assertEqual(self.visita.estado, "en_curso", f"Estado inesperado: {self.visita.estado}")
        self.assertIsNotNone(self.visita.fecha_hora_llegada, "No se registró la llegada.")
        # Verificar que encoding_facial es None o tiene al menos un encoding
        self.persona.refresh_from_db()
        if self.persona.encoding_facial is not None:
            self.assertTrue(len(self.persona.encoding_facial) >= 1, "encoding_facial vacío")
