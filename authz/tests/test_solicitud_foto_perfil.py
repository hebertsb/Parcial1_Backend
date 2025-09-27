
import os
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from core.models.propiedades_residentes import Vivienda
from authz.models import SolicitudRegistroPropietario

class SolicitudFotoPerfilDetalleTest(APITestCase):
    def setUp(self):
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

    def test_crear_y_ver_foto_perfil_en_detalle(self):
        url = reverse('registro-solicitud-propietario')
        image_path = os.path.join(settings.BASE_DIR, "authz", "tests", "media", "1.jpg")
        with open(image_path, "rb") as img_file:
            image = SimpleUploadedFile(
                "test.jpg", img_file.read(), content_type="image/jpeg"
            )
            data = {
                "nombres": "Juan",
                "apellidos": "Pérez",
                "documento_identidad": "12345678",
                "fecha_nacimiento": "1990-01-01",
                "email": "juan.perez@example.com",
                "telefono": "123456789",
                "numero_casa": "A-101",
                "password": "TestPassword123",
                "password_confirm": "TestPassword123",
                "confirm_password": "TestPassword123",
                "foto_perfil": image,
                "acepta_terminos": True,
                "acepta_tratamiento_datos": True
            }
            response = self.client.post(url, data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertTrue(
                SolicitudRegistroPropietario.objects.filter(email="juan.perez@example.com").exists()
            )
            solicitud = SolicitudRegistroPropietario.objects.get(email="juan.perez@example.com")
            self.assertIsNotNone(solicitud.foto_perfil)

            # Ahora consulta el detalle (simulando admin autenticado)
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin = User.objects.create_user(
                email="admin@example.com",
                password="adminpass",
                is_staff=True,
                is_superuser=True
            )
            # Crear y asignar el rol 'Administrador'
            from authz.models import Rol
            rol_admin, _ = Rol.objects.get_or_create(nombre="Administrador")
            admin.roles.add(rol_admin)
            self.client.force_authenticate(user=admin)
            detalle_url = reverse('detalle-solicitud', args=[solicitud.id])
            detalle_response = self.client.get(detalle_url)
            self.assertEqual(detalle_response.status_code, status.HTTP_200_OK)
            self.assertIn('foto_perfil', detalle_response.data)
            self.assertTrue(detalle_response.data['foto_perfil'])
            print("URL de la imagen en respuesta:", detalle_response.data['foto_perfil'])
