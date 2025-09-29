#!/usr/bin/env python3
"""
Script para corregir errores comunes de Pylance en archivos de prueba
"""

import os
import re
import glob

def corregir_response_unbound(content):
    """Corrige el problema de variable response posiblemente desvinculada"""
    
    # Patrón para encontrar bloques try con requests
    pattern = r'(\s+)try:\s*\n((?:\1\s+.*\n)*?)(\s+)except.*?:'
    
    def replace_try_block(match):
        indent = match.group(1)
        try_content = match.group(2)
        except_indent = match.group(3)
        
        # Si contiene requests y no inicializa response, agregarlo
        if 'requests.' in try_content and 'response = None' not in try_content:
            new_content = f"{indent}response = None  # Inicializar response\n{indent}try:\n{try_content}{except_indent}except"
            return new_content
        
        return match.group(0)
    
    # Aplicar corrección
    corrected = re.sub(pattern, replace_try_block, content, flags=re.MULTILINE)
    
    # También corregir uso de response sin verificación
    corrected = re.sub(
        r'(\s+)(response\.(status_code|headers|text|json\(\)))',
        r'\1if response is not None:\n\1    \2',
        corrected
    )
    
    return corrected

def corregir_function_member_access(content):
    """Corrige el acceso a atributos de función que pueden no existir"""
    
    # Reemplazar acceso directo a func.cls
    content = re.sub(
        r'(\s+)print\(f".*?{([^}]*func\.[^}]+)}.*?"\)',
        lambda m: m.group(1) + 'print(f"Atributos disponibles: {[attr for attr in dir(func) if not attr.startswith(\'_\')][:5]}...")',
        content
    )
    
    # Reemplazar hasattr con getattr seguro
    content = re.sub(
        r'if hasattr\(([^,]+), \'([^\']+)\'\):\s*\n\s+print\(f".*?{\1\.\2}.*?"\)',
        r'if hasattr(\1, \'\2\'):\n            attr_value = getattr(\1, \'\2\', None)\n            print(f"   \2: {attr_value}")',
        content
    )
    
    return content

def corregir_archivo(filepath):
    """Corrige un archivo específico"""
    print(f"🔧 Corrigiendo: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar correcciones
        content = corregir_response_unbound(content)
        content = corregir_function_member_access(content)
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Archivo corregido")
            return True
        else:
            print(f"  ℹ️ No necesita correcciones")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 CORRIGIENDO ERRORES EN ARCHIVOS DE PRUEBA")
    print("=" * 50)
    
    # Patrones de archivos a revisar
    patterns = [
        "test_*.py",
        "prueba_*.py",
        "*_test.py",
        "verificar_*.py"
    ]
    
    archivos_corregidos = 0
    archivos_revisados = 0
    
    for pattern in patterns:
        for filepath in glob.glob(pattern):
            if os.path.isfile(filepath):
                archivos_revisados += 1
                if corregir_archivo(filepath):
                    archivos_corregidos += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"  📁 Archivos revisados: {archivos_revisados}")
    print(f"  🔧 Archivos corregidos: {archivos_corregidos}")
    print(f"  ✅ Archivos sin cambios: {archivos_revisados - archivos_corregidos}")
    
    if archivos_corregidos > 0:
        print("\n🎉 ¡Correcciones aplicadas exitosamente!")
    else:
        print("\n✨ No se encontraron errores que corregir")

if __name__ == '__main__':
    main()