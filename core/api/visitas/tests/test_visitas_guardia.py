from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models.propiedades_residentes import Visita, Vivienda
from authz.models import Persona, Rol
import base64

class VisitasGuardiaEndpointTest(APITestCase):
    def setUp(self):
        # Crear vivienda y persona autorizante
        vivienda = Vivienda.objects.create(
            numero_casa="B-202",
            bloque="B",
            tipo_vivienda="departamento",
            metros_cuadrados=80,
            tarifa_base_expensas=800,
            tipo_cobranza="por_casa",
            estado="activa"
        )
        self.persona_autorizante = Persona.objects.create(
            nombre="Propietario",
            apellido="Test",
            documento_identidad="99999999",
            telefono="123456789",
            email="propietario@example.com",
            tipo_persona="propietario"
        )
        # Crear usuario guardia
        User = get_user_model()
        self.guardia = User.objects.create_user(
            email="guardia@example.com",
            password="guardiapass",
            is_staff=True
        )
        rol_guardia, _ = Rol.objects.get_or_create(nombre="Seguridad")
        self.guardia.roles.add(rol_guardia)
        self.client.force_authenticate(user=self.guardia)
        # Crear visita programada con fotos de reconocimiento
        foto_b64 = base64.b64encode(b"fake-image-bytes").decode()
        self.visita = Visita.objects.create(
            persona_autorizante=self.persona_autorizante,
            nombre_visitante="Visitante Uno",
            documento_visitante="1234567",
            telefono_visitante="5555555",
            motivo_visita="Reunión",
            estado="programada",
            fotos_reconocimiento_urls=["https://dropbox.com/fake1.jpg", "https://dropbox.com/fake2.jpg"]
        )

    def test_guardia_ve_visitas_pendientes(self):
        url = reverse('visita-pendientes-guardia')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)
        visita = response.data[0]
        self.assertIn('fotos_reconocimiento_urls', visita)
        self.assertEqual(visita['estado'], 'programada')
        print("Visitas pendientes para guardia:", response.data)
