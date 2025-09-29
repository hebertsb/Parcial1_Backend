#!/usr/bin/env python
"""
Script para verificar usuarios con reconocimiento facial
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import Copropietarios, ReconocimientoFacial

def mostrar_usuarios():
    """Mostrar todos los usuarios con reconocimiento facial"""
    
    print("🔍 USUARIOS CON RECONOCIMIENTO FACIAL")
    print("=" * 50)
    
    # Obtener usuarios con reconocimiento facial activo
    usuarios_con_reconocimiento = ReconocimientoFacial.objects.filter(activo=True).select_related('copropietario')
    
    if not usuarios_con_reconocimiento:
        print("❌ No hay usuarios con reconocimiento facial activo")
        return
    
    for i, reconocimiento in enumerate(usuarios_con_reconocimiento, 1):
        copropietario = reconocimiento.copropietario
        print(f"\n👤 USUARIO {i}:")
        print(f"   📛 Nombre: {copropietario.nombres} {copropietario.apellidos}")
        print(f"   📄 Documento: {copropietario.numero_documento}")
        print(f"   🏠 Casa: {copropietario.unidad_residencial}")
        print(f"   📧 Email: {copropietario.email}")
        print(f"   📞 Teléfono: {copropietario.telefono}")
        print(f"   🔒 Estado: {'ACTIVO' if reconocimiento.activo else 'INACTIVO'}")
        print(f"   🎯 Confianza: {reconocimiento.confianza_enrolamiento}%")
        print(f"   🤖 Proveedor: {reconocimiento.proveedor_ia}")
    
    # Estadísticas generales
    total_usuarios = Copropietarios.objects.count()
    total_con_reconocimiento = usuarios_con_reconocimiento.count()
    
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   👥 Total usuarios: {total_usuarios}")
    print(f"   🔍 Con reconocimiento activo: {total_con_reconocimiento}")
    print(f"   📈 Porcentaje con reconocimiento: {(total_con_reconocimiento/total_usuarios*100):.1f}%")

if __name__ == '__main__':
    mostrar_usuarios()