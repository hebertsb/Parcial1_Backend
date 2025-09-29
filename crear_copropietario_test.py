#!/usr/bin/env python3
"""
Script para crear copropietario asociado al usuario de prueba
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios

def crear_copropietario_para_usuario():
    """Crear copropietario asociado al usuario de prueba"""
    
    email_usuario = "propietario.test@example.com"
    
    print(f"🔧 CREANDO COPROPIETARIO PARA: {email_usuario}")
    print("=" * 60)
    
    try:
        # Obtener usuario
        usuario = Usuario.objects.get(email=email_usuario)
        print(f"✅ Usuario encontrado: {usuario.email}")
        
        # Verificar si ya tiene copropietario
        copropietario_existente = Copropietarios.objects.filter(usuario_sistema_id=usuario.id).first()
        
        if copropietario_existente:
            print(f"✅ Ya existe copropietario asociado:")
            print(f"   • ID: {copropietario_existente.id}")
            print(f"   • Nombre: {copropietario_existente.nombres} {copropietario_existente.apellidos}")
            print(f"   • Unidad: {copropietario_existente.unidad_residencial}")
            return copropietario_existente
        
        # Crear nuevo copropietario
        import random
        numero_doc = f"TEST{random.randint(10000000, 99999999)}"
        copropietario = Copropietarios.objects.create(
            nombres="Test",
            apellidos="Propietario",
            numero_documento=numero_doc,
            tipo_documento="CC",
            telefono="3001234567",
            email=usuario.email,
            unidad_residencial="Casa 101",
            tipo_residente="Propietario",
            usuario_sistema=usuario,
            activo=True
        )
        
        print(f"✅ Copropietario creado exitosamente:")
        print(f"   • ID: {copropietario.id}")
        print(f"   • Nombre: {copropietario.nombres} {copropietario.apellidos}")
        print(f"   • Documento: {copropietario.numero_documento}")
        print(f"   • Unidad: {copropietario.unidad_residencial}")
        print(f"   • Usuario asociado: {copropietario.usuario_sistema.email}")
        
        return copropietario
        
    except Usuario.DoesNotExist:
        print(f"❌ Usuario no encontrado: {email_usuario}")
        return None

if __name__ == "__main__":
    print("🏠 CONFIGURANDO COPROPIETARIO PARA PRUEBAS")
    print("=" * 60)
    
    copropietario = crear_copropietario_para_usuario()
    
    if copropietario:
        print(f"\n✅ CONFIGURACIÓN COMPLETA")
        print("=" * 60)
        print("🎯 DATOS PARA PRUEBAS:")
        print(f"   • Email: {copropietario.usuario_sistema.email}")
        print(f"   • Password: testing123")
        print(f"   • Copropietario ID: {copropietario.id}")
        print(f"   • Unidad: {copropietario.unidad_residencial}")
        print("\n🚀 Los endpoints del panel ya están listos para usar")
    else:
        print("\n❌ Error en la configuración")