"""
Tests para el sistema de reconocimiento facial
"""

import io
import json
import base64
from unittest.mock import patch, MagicMock
from PIL import Image
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from seguridad.models import (
    Roles, Usuarios, Copropietarios, ReconocimientoFacial, BitacoraAcciones
)


class ModelsTestCase(TestCase):
    """Tests para los modelos"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.rol = Roles.objects.create(
            nombre='Test Role',
            descripcion='Rol de prueba'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.usuario = Usuarios.objects.create(
            user=self.user,
            rol=self.rol,
            telefono='+573001234567'
        )
        
        self.copropietario = Copropietarios.objects.create(
            nombres='Juan',
            apellidos='Pérez',
            numero_documento='12345678',
            tipo_documento='CC',
            telefono='+573009876543',
            email='juan.perez@test.com',
            unidad_residencial='Apto 101'
        )
    
    def test_rol_creation(self):
        """Test creación de rol"""
        self.assertEqual(self.rol.nombre, 'Test Role')
        self.assertTrue(self.rol.activo)
        
    def test_usuario_creation(self):
        """Test creación de usuario"""
        self.assertEqual(self.usuario.user.username, 'testuser')
        self.assertEqual(self.usuario.rol, self.rol)
        
    def test_copropietario_creation(self):
        """Test creación de copropietario"""
        self.assertEqual(self.copropietario.nombre_completo, 'Juan Pérez')
        self.assertEqual(self.copropietario.numero_documento, '12345678')
        
    def test_reconocimiento_facial_creation(self):
        """Test creación de reconocimiento facial"""
        reconocimiento = ReconocimientoFacial.objects.create(
            copropietario=self.copropietario,
            proveedor_ia='Local',
            vector_facial='test_vector',
            activo=True
        )
        
        self.assertEqual(reconocimiento.copropietario, self.copropietario)
        self.assertEqual(reconocimiento.proveedor_ia, 'Local')
        self.assertTrue(reconocimiento.activo)


class FaceRecognitionAPITestCase(APITestCase):
    """Tests para la API de reconocimiento facial"""
    
    def setUp(self):
        """Configuración inicial"""
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Crear rol y usuario
        self.rol = Roles.objects.create(nombre='Operador')
        self.usuario = Usuarios.objects.create(
            user=self.user,
            rol=self.rol
        )
        
        # Crear copropietario
        self.copropietario = Copropietarios.objects.create(
            nombres='Test',
            apellidos='User',
            numero_documento='12345678',
            tipo_documento='CC',
            unidad_residencial='Apto 101'
        )
        
        # Obtener token JWT
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Configurar autenticación
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Crear imagen de prueba
        self.test_image = self._create_test_image()
    
    def _create_test_image(self):
        """Crea una imagen de prueba"""
        img = Image.new('RGB', (200, 200), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_face_enroll_without_auth(self):
        """Test enrolamiento sin autenticación"""
        self.client.credentials()  # Remover credenciales
        
        url = reverse('seguridad:face-enroll')
        response = self.client.post(url, {
            'copropietario_id': self.copropietario.id,
            'imagen': self.test_image
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_face_enroll_invalid_copropietario(self):
        """Test enrolamiento con copropietario inválido"""
        url = reverse('seguridad:face-enroll')
        response = self.client.post(url, {
            'copropietario_id': 9999,  # ID inexistente
            'imagen': self.test_image
        }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_face_status_not_enrolled(self):
        """Test estado sin enrolamiento"""
        url = reverse('seguridad:face-status', args=[self.copropietario.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['enrolado'])
        self.assertIsNone(response.data['proveedor'])


class BitacoraTestCase(TestCase):
    """Tests para la bitácora de acciones"""
    
    def setUp(self):
        """Configuración inicial"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.rol = Roles.objects.create(nombre='Test Role')
        self.usuario = Usuarios.objects.create(user=self.user, rol=self.rol)
        
        self.copropietario = Copropietarios.objects.create(
            nombres='Test',
            apellidos='User',
            numero_documento='12345678',
            unidad_residencial='Apto 101'
        )
    
    def test_bitacora_creation(self):
        """Test creación de registro en bitácora"""
        from seguridad.models import fn_bitacora_log
        
        fn_bitacora_log(
            tipo_accion='ENROLL_FACE',
            descripcion='Test de enrolamiento',
            usuario=self.usuario,
            copropietario=self.copropietario,
            proveedor_ia='Local',
            confianza=0.9
        )
        
        # Verificar que se creó el registro
        bitacora = BitacoraAcciones.objects.filter(
            tipo_accion='ENROLL_FACE'
        ).first()
        
        self.assertIsNotNone(bitacora)
        self.assertEqual(bitacora.usuario, self.usuario)
        self.assertEqual(bitacora.copropietario, self.copropietario)
        self.assertEqual(bitacora.proveedor_ia, 'Local')
        self.assertEqual(bitacora.confianza, 0.9)
