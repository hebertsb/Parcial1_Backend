#!/usr/bin/env python
"""
Crear reconocimiento facial usando el modelo directamente
"""

import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial
import json

def crear_reconocimiento():
    try:
        usuario = Usuario.objects.get(id=12)
        copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
        
        # Verificar si ya existe
        existing = ReconocimientoFacial.objects.filter(copropietario=copropietario).first()
        if existing:
            print(f"Ya existe ReconocimientoFacial ID {existing.id} para copropietario {copropietario.id}")
            return existing
        
        # Crear nuevo registro con todos los campos necesarios
        reconocimiento = ReconocimientoFacial(
            copropietario=copropietario,
            proveedor_ia='Local',
            vector_facial='demo_vector_usuario_12',
            activo=True,
            confianza_enrolamiento=0.95,
            intentos_verificacion=0
        )
        
        # Si el modelo tiene fotos_urls, agregarlas
        if hasattr(reconocimiento, 'fotos_urls'):
            reconocimiento.fotos_urls = json.dumps([
                'https://demo.com/foto1.jpg',
                'https://demo.com/foto2.jpg', 
                'https://demo.com/foto3.jpg',
                'https://demo.com/foto4.jpg',
                'https://demo.com/foto5.jpg'
            ])
        
        reconocimiento.save()
        
        print(f'✅ ReconocimientoFacial creado exitosamente!')
        print(f'   ID: {reconocimiento.id}')
        print(f'   Usuario: {usuario.email}')
        print(f'   Copropietario: {copropietario.nombres} {copropietario.apellidos}')
        print(f'   Activo: {reconocimiento.activo}')
        
        return reconocimiento
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    crear_reconocimiento()