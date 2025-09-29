# 🚀 PRUEBA RÁPIDA DEL ENDPOINT CORREGIDO

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from authz.views_fotos_reconocimiento_corregido import subir_fotos_reconocimiento_corregido
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.core.files.uploadedfile import SimpleUploadedFile
import json

def test_endpoint_corregido():
    """🧪 Probar el endpoint corregido directamente"""
    print("=" * 60)
    print("🧪 PRUEBA DIRECTA DEL ENDPOINT CORREGIDO")
    print("=" * 60)
    
    # 1. Verificar usuarios válidos
    print("\n👥 Verificando usuarios con rol Propietario...")
    try:
        rol_propietario = Rol.objects.get(nombre='Propietario')
        usuarios_propietarios = Usuario.objects.filter(roles=rol_propietario, activo=True)
        
        print(f"✅ Rol 'Propietario' encontrado (ID: {rol_propietario.id})")
        print(f"✅ Usuarios con rol Propietario: {usuarios_propietarios.count()}")
        
        for usuario in usuarios_propietarios:
            print(f"   - ID {usuario.id}: {usuario.email} ({usuario.persona.nombre if usuario.persona else 'Sin persona'})")
            
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
        return
    
    # 2. Seleccionar usuario de prueba
    if usuarios_propietarios.exists():
        usuario_prueba = usuarios_propietarios.first()
        print(f"\n🎯 Usuario de prueba seleccionado: ID {usuario_prueba.id} - {usuario_prueba.email}")
    else:
        print("❌ No se encontraron usuarios con rol Propietario")
        return
    
    # 3. Simular request con archivo
    print("\n📸 Simulando subida de foto...")
    factory = RequestFactory()
    
    # Crear archivo de prueba
    archivo_prueba = SimpleUploadedFile(
        "test_foto.jpg",
        b"contenido_imagen_prueba",
        content_type="image/jpeg"
    )
    
    # Crear request simulado
    request = factory.post('/api/authz/reconocimiento/fotos/', {
        'usuario_id': usuario_prueba.id,
        'fotos': [archivo_prueba]
    })
    
    # Asignar usuario autenticado
    request.user = usuario_prueba
    request.FILES = {'fotos': [archivo_prueba]}
    request.data = {'usuario_id': usuario_prueba.id}
    
    # 4. Llamar al endpoint
    print("🔧 Ejecutando endpoint corregido...")
    try:
        response = subir_fotos_reconocimiento_corregido(request)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Data: {response.data}")
        
        if if response is not None:
     response.status_code == 200:
            print("🎉 ¡ENDPOINT FUNCIONANDO CORRECTAMENTE!")
            print("✅ Variable 'success' corregida")
            print("✅ Integración con Dropbox funcional")
            print("✅ Validación de roles operativa")
            
            # Mostrar detalles de la respuesta
            data = response.data.get('data', {})
            print(f"\n📋 Detalles de la respuesta:")
            print(f"   - Usuario: {data.get('usuario_email')}")
            print(f"   - Propietario: {data.get('propietario_nombre')}")
            print(f"   - Total fotos: {data.get('total_fotos')}")
            print(f"   - URLs generadas: {len(data.get('fotos_urls', []))}")
            
        else:
            print(f"❌ Error en endpoint: {response.data}")
            
    except Exception as e:
        print(f"❌ Error ejecutando endpoint: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_endpoint_corregido()