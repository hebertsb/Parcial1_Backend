import os
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.propiedades_residentes import Visita
from authz.models import Persona

class VisitaDropboxUploadTest(APITestCase):
    def setUp(self):
        # Crear persona autorizante
        self.persona = Persona.objects.create(
            nombre="Propietario",
            apellido="Test",
            documento_identidad="99999999",
            telefono="123456789",
            email="propietario@example.com",
            fecha_nacimiento="1990-01-01",
            tipo_persona="propietario"
        )
        # Autenticar como usuario relacionado a persona
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(email="user@example.com", password="testpass")
        self.user.persona = self.persona
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_crear_visita_con_foto_dropbox(self):
        url = reverse('visita-list')
        image_path = os.path.join(settings.BASE_DIR, "authz", "tests", "media", "2.jpg")
        with open(image_path, "rb") as img_file:
            image = SimpleUploadedFile(
                "test.jpg", img_file.read(), content_type="image/jpeg"
            )
        data = {
            "nombre_visitante": "Juan Visitante",
            "documento_visitante": "12345678",
            "telefono_visitante": "5555555",
            "motivo_visita": "Reunión",
            "fecha_hora_programada": "2025-09-25T10:00:00Z",
            "foto_ingreso": image
        }
        response = self.client.post(url, data, format='multipart')
        print("RESPONSE DATA:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        visita = Visita.objects.get(nombre_visitante="Juan Visitante")
        self.assertTrue(visita.foto_ingreso_url)
        print("URL Dropbox:", visita.foto_ingreso_url)
