"""
Tests para el sistema de reconocimiento facial
"""

import io
import json
import base64
from unittest.mock import patch, MagicMock
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Optional, cast

from seguridad.models import (
    Copropietarios, ReconocimientoFacial, BitacoraAcciones, fn_bitacora_log
)
from authz.models import Usuario, Rol


class ModelsTestCase(TestCase):
    """Tests para los modelos"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        self.rol = Rol.objects.create(
            nombre='Test Role',
            descripcion='Rol de prueba'
        )
        
        self.usuario = Usuario.objects.create_user(
            email='test@test.com',
            password='testpass123'
        )
        self.usuario.roles.add(self.rol)
        
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
        # Crear rol y usuario
        self.rol = Rol.objects.create(nombre='Operador')
        self.usuario = Usuario.objects.create_user(
            email='testuser@test.com',
            password='testpass123'
        )
        self.usuario.roles.add(self.rol)
        
        # Crear copropietario
        self.copropietario = Copropietarios.objects.create(
            nombres='Test',
            apellidos='User',
            numero_documento='12345678',
            tipo_documento='CC',
            unidad_residencial='Apto 101'
        )
        
        # Obtener token JWT
        refresh = RefreshToken.for_user(self.usuario)
        self.access_token = str(refresh.access_token)
        
        # Configurar autenticación
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
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
        self.client.credentials()  # Remover credenciales  # type: ignore
        
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
        # APITestCase provides response.data attribute
        self.assertFalse(response.data['enrolado'])  # type: ignore
        self.assertIsNone(response.data['proveedor'])  # type: ignore


class BitacoraTestCase(TestCase):
    """Tests para la bitácora de acciones"""
    
    def setUp(self):
        """Configuración inicial"""
        self.rol = Rol.objects.create(nombre='Test Role')
        self.usuario = Usuario.objects.create_user(
            email='testuser@test.com',
            password='testpass123'
        )
        self.usuario.roles.add(self.rol)
        
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
        # Usar assert para que Pylance entienda que bitacora no es None
        assert bitacora is not None
        self.assertEqual(bitacora.usuario, self.usuario)
        self.assertEqual(bitacora.copropietario, self.copropietario)
        self.assertEqual(bitacora.proveedor_ia, 'Local')
        self.assertEqual(bitacora.confianza, 0.9)
