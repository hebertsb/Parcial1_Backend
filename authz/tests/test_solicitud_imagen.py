import os
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.propiedades_residentes import Vivienda
from authz.models import SolicitudRegistroPropietario

class SolicitudRegistroPropietarioImageTest(APITestCase):
    def test_crear_solicitud_con_varias_imagenes(self):
        # Crear vivienda válida
        Vivienda.objects.create(
            numero_casa="A-101",
            bloque="A",
            tipo_vivienda="casa",
            metros_cuadrados=100,
            tarifa_base_expensas=1000,
            tipo_cobranza="por_casa",
            estado="activa"
        )

        url = reverse('registro-solicitud-propietario')

        # Leer varias imágenes y convertirlas a base64
        base_dir = os.path.join(settings.BASE_DIR, "authz", "tests", "media")
        image_files = ["9.jpg", "10.jpg", "11.jpg", "12.jpg", "13.jpg"]  # Puedes agregar más imágenes si tienes
        fotos_base64 = []
        import base64
        for img_name in image_files:
            img_path = os.path.join(base_dir, img_name)
            with open(img_path, "rb") as img_file:
                img_bytes = img_file.read()
                img_b64 = base64.b64encode(img_bytes).decode('utf-8')
                fotos_base64.append(f"data:,image/jpeg;base64,{img_b64}")

        data = {
            "nombres": "Douglas",
            "apellidos": "Seviche",
            "documento_identidad": "12345678",
            "fecha_nacimiento": "1990-01-01",
            "email": "douglas.seviche@example.com",
            "telefono": "123456789",
            "numero_casa": "A-101",
            "password": "TestPassword123",
            "password_confirm": "TestPassword123",
            "confirm_password": "TestPassword123",
            "fotos_base64": fotos_base64,
            "acepta_terminos": True,
            "acepta_tratamiento_datos": True
        }
        response = self.client.post(url, data, format='json')
        print("RESPONSE DATA:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            SolicitudRegistroPropietario.objects.filter(email="douglas.seviche@example.com").exists()
        )
        solicitud = SolicitudRegistroPropietario.objects.get(email="douglas.seviche@example.com")
        self.assertIsNotNone(solicitud.foto_perfil)
