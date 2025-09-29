#!/usr/bin/env python3
"""
Script para corregir las referencias incorrectas a persona_id en views_propietario.py
"""

import re

def corregir_views_propietario():
    """Corregir referencias a persona_id por usuario_sistema_id"""
    
    archivo = "authz/views_propietario.py"
    
    # Leer el archivo
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Hacer el reemplazo
    contenido_corregido = contenido.replace('persona_id=usuario.id', 'usuario_sistema_id=usuario.id')
    
    # Verificar que se hicieron cambios
    if contenido != contenido_corregido:
        # Escribir el archivo corregido
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(contenido_corregido)
        
        print("✅ Corregido authz/views_propietario.py")
        print("   • persona_id → usuario_sistema_id")
        return True
    else:
        print("❌ No se encontraron ocurrencias para corregir")
        return False

if __name__ == "__main__":
    print("🔧 CORRIGIENDO REFERENCIAS EN VIEWS_PROPIETARIO.PY")
    print("=" * 60)
    
    corregido = corregir_views_propietario()
    
    if corregido:
        print("\n✅ CORRECCIÓN COMPLETADA")
        print("Los endpoints del panel de propietarios ahora usan el campo correcto")
    else:
        print("\n⚠️ NO SE ENCONTRARON CORRECCIONES NECESARIAS")