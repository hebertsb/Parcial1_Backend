from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from .models import Usuario, Persona, Rol

class UsuarioFotoPerfilFlowTest(TestCase):
	def setUp(self):
		self.client = APIClient()
		# Crear rol y persona
		self.rol = Rol.objects.create(nombre="Propietario")
		self.persona = Persona.objects.create(
			nombre="Juan",
			apellido="Pérez",
			documento_identidad="12345678",
			telefono="123456789",
			email="juan@example.com",
			fecha_nacimiento="1990-01-01",
			genero="M",
			pais="Argentina",
			tipo_persona="propietario",
			direccion="Calle Falsa 123",
			activo=True
		)
		self.usuario = Usuario.objects.create(
			email="juan@example.com",
			persona=self.persona,
			estado="ACTIVO"
		)
		self.usuario.roles.add(self.rol)
		self.usuario.set_password("testpassword")
		self.usuario.save()

	def test_foto_perfil_exposed_in_me_endpoint(self):
		# Autenticar usuario
		response = self.client.post(reverse('token_obtain_pair'), {
			'email': 'juan@example.com',
			'password': 'testpassword'
		})
		self.assertEqual(response.status_code, 200)
		access = response.data['access']
		self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
		# Consultar endpoint /me
		response = self.client.get(reverse('usuario-me'))
		self.assertEqual(response.status_code, 200)
		# Verificar que foto_perfil está presente
		data = response.data
		# Puede estar en persona o en campos anidados
		self.assertIn('persona', data)
		self.assertIn('foto_perfil', data['persona'])

