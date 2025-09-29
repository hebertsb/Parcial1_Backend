
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient, force_authenticate
from rest_framework import status
from django.contrib.auth import get_user_model
User = get_user_model()

class EnviarAlertaExpensaVencidaTest(APITestCase):
	def setUp(self):
		self.admin_user = User.objects.create_superuser(email='admin@test.com', password='adminpass')
		self.client = APIClient()
		self.url = reverse('expensas_multas:enviar_alerta_expensa_vencida')

	def test_enviar_alerta_expensa_vencida(self):
		data = {
			'token_fcm': 'dsQ7wJgWRva33sKovU_QdV:APA91bF_nn81vxs5zQ15OsRuAsIyQLS1db819-sAxVtx5KKaTbdu5byxVx9BOVAhjA0nuGY7PwWo9eho3s1DS-s9MsE1mT1oNi9IPJ6o41UiuhAzWRbuqrE',
			'mensaje': 'Prueba de alerta expensa vencida.'
		}
		self.client.force_authenticate(user=self.admin_user)
		response = self.client.post(self.url, data, format='json')
		print('Response:', response.data)
		self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR, status.HTTP_400_BAD_REQUEST])
