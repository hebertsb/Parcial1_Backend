from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import FamiliarPropietario, Persona
from io import BytesIO
from PIL import Image

def get_test_image():
    # Genera una imagen en memoria
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color = 'red')
    image.save(file, 'JPEG')
    file.name = 'test.jpg'
    file.seek(0)
    return file

class RegistroFamiliarPropietarioTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(email='propietario@test.com', password='12345678')
        self.client.force_authenticate(user=self.user)

    def test_registro_familiar_con_imagen(self):
        url = reverse('authz:familiarpropietario-list')
        data = {
            "propietario": self.user.id,
            "parentesco": "hijo",
            "parentesco_descripcion": "Hijo mayor",
            "autorizado_acceso": True,
            "puede_autorizar_visitas": False,
            "observaciones": "Prueba de registro",
            "nombre": "Juan",
            "apellido": "Pérez",
            "documento_identidad": "1234567890",
            "telefono": "5551234",
            "email": "juan@test.com",
            "fecha_nacimiento": "2000-01-01",
            "genero": "M",
            "pais": "Bolivia",
            "direccion": "Calle Falsa 123",
            "foto_perfil": get_test_image(),
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('persona', response.data)
        self.assertIn('foto_perfil', response.data['persona'])
        self.assertTrue(response.data['persona']['foto_perfil'])
