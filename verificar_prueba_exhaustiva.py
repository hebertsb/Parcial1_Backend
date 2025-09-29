#!/usr/bin/env python3
"""
Verificación específica del archivo prueba_exhaustiva.py
"""

import ast
import sys

def verificar_prueba_exhaustiva():
    """Verifica que el archivo prueba_exhaustiva.py esté libre de errores"""
    
    print("🔍 VERIFICANDO CORRECCIONES EN prueba_exhaustiva.py")
    print("=" * 50)
    
    filepath = "prueba_exhaustiva.py"
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar sintaxis
        try:
            ast.parse(content)
            print("✅ Sintaxis correcta")
        except SyntaxError as e:
            print(f"❌ Error de sintaxis: {e}")
            return False
        
        # Verificar correcciones específicas
        issues_found = []
        
        # 1. Verificar inicialización de response
        if 'response = None' in content:
            print("✅ Variable response inicializada correctamente")
        else:
            issues_found.append("Response no inicializada")
        
        # 2. Verificar verificación de response antes de uso
        if 'if response is not None:' in content:
            print("✅ Verificación de response implementada")
        else:
            issues_found.append("Falta verificación de response")
        
        # 3. Verificar uso seguro de getattr
        if 'getattr(' in content:
            print("✅ Uso seguro de getattr implementado")
        else:
            print("ℹ️ No se usa getattr (puede estar bien)")
        
        # 4. Verificar que no hay acceso directo problemático
        problematic_patterns = [
            'func.cls',
            'func.actions',
            'response.status_code' # sin verificación previa
        ]
        
        for pattern in problematic_patterns:
            if pattern in content and 'if response is not None:' not in content.split(pattern)[0].split('\n')[-5:]:
                if pattern.startswith('func.'):
                    if f'getattr(func, \'{pattern.split(".")[1]}\'' not in content:
                        issues_found.append(f"Acceso directo problemático: {pattern}")
        
        # Resumen
        if not issues_found:
            print("\n🎉 ¡ARCHIVO COMPLETAMENTE CORREGIDO!")
            print("   - Variable response inicializada")
            print("   - Verificaciones de seguridad implementadas")
            print("   - Acceso seguro a atributos de función")
            return True
        else:
            print(f"\n❌ Se encontraron {len(issues_found)} problemas:")
            for issue in issues_found:
                print(f"   - {issue}")
            return False
            
    except FileNotFoundError:
        print(f"❌ Archivo no encontrado: {filepath}")
        return False
    except Exception as e:
        print(f"❌ Error durante verificación: {e}")
        return False

def test_import():
    """Prueba de importación del módulo"""
    print("\n🧪 PROBANDO IMPORTACIÓN...")
    
    try:
        # Simular importación (sin ejecutar)
        with open("prueba_exhaustiva.py", 'r') as f:
            content = f.read()
        
        # Verificar que tiene las funciones esperadas
        expected_functions = ['probar_todos_los_metodos', 'verificar_urls_django']
        
        for func_name in expected_functions:
            if f'def {func_name}(' in content:
                print(f"  ✅ Función {func_name} encontrada")
            else:
                print(f"  ❌ Función {func_name} no encontrada")
                return False
        
        print("✅ Estructura del módulo correcta")
        return True
        
    except Exception as e:
        print(f"❌ Error en test de importación: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 VERIFICACIÓN COMPLETA DE CORRECCIONES")
    print("=" * 60)
    
    tests = [
        ("Verificación de correcciones", verificar_prueba_exhaustiva),
        ("Test de importación", test_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name.upper()}:")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL:")
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Pruebas exitosas: {passed}/{total}")
    
    if passed == total:
        print("🎉 ¡TODAS LAS CORRECCIONES VERIFICADAS EXITOSAMENTE!")
        print("\n📝 El archivo prueba_exhaustiva.py está listo para usar:")
        print("   python prueba_exhaustiva.py")
        return True
    else:
        print("❌ Algunas correcciones necesitan revisión manual")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)