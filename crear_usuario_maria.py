#!/usr/bin/env python
"""
Script para crear usuario adicional con reconocimiento facial
"""
import os
import sys
import django
import json
import random

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import Copropietarios, ReconocimientoFacial

def crear_usuario_maria():
    """Crear usuario Maria Elena con reconocimiento facial"""
    
    # Verificar si ya existe
    if Copropietarios.objects.filter(numero_documento='TEST002').exists():
        print("❌ Usuario Maria Elena ya existe")
        return
    
    try:
        # Crear copropietario
        maria = Copropietarios.objects.create(
            nombres='Maria Elena',
            apellidos='Rodriguez Silva',
            numero_documento='TEST002',
            tipo_documento='CC',
            telefono='72345678',
            email='maria@test.com',
            unidad_residencial='Casa 5',
            tipo_residente='Propietario'
        )
        
        # Crear reconocimiento facial
        reconocimiento = ReconocimientoFacial.objects.create(
            copropietario=maria,
            proveedor_ia='Local',
            vector_facial=json.dumps([random.uniform(-1, 1) for _ in range(128)]),
            imagen_referencia_url='https://example.com/maria.jpg',
            activo=True,
            confianza_enrolamiento=88.5
        )
        
        print(f"✅ Usuario creado exitosamente: {maria.nombres} {maria.apellidos}")
        print(f"📄 Documento: {maria.numero_documento}")
        print(f"🏠 Casa: {maria.unidad_residencial}")
        print(f"📧 Email: {maria.email}")
        print(f"🔒 Reconocimiento facial: {'ACTIVO' if reconocimiento.activo else 'INACTIVO'}")
        
        # Mostrar estadísticas
        total_usuarios = Copropietarios.objects.count()
        total_con_reconocimiento = ReconocimientoFacial.objects.filter(activo=True).count()
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"👥 Total usuarios: {total_usuarios}")
        print(f"🔍 Con reconocimiento activo: {total_con_reconocimiento}")
        
    except Exception as e:
        print(f"❌ Error creando usuario: {str(e)}")

if __name__ == '__main__':
    crear_usuario_maria()