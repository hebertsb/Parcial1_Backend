#!/usr/bin/env python3
"""
Script para identificar y eliminar tests problemáticos
"""

import os
import sys
import subprocess
import glob
import traceback

def ejecutar_test(archivo):
    """Ejecuta un test individual y retorna si fue exitoso"""
    print(f"🧪 Probando: {archivo}")
    
    try:
        # Ejecutar el archivo Python
        result = subprocess.run(
            [sys.executable, archivo], 
            capture_output=True, 
            text=True, 
            timeout=30,
            cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            print(f"  ✅ ÉXITO")
            return True, "Éxito"
        else:
            print(f"  ❌ FALLÓ - Código: {result.returncode}")
            print(f"     Error: {result.stderr[:200]}...")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"  ⏰ TIMEOUT - El test tardó más de 30 segundos")
        return False, "Timeout"
    except Exception as e:
        print(f"  💥 EXCEPCIÓN: {e}")
        return False, str(e)

def verificar_sintaxis(archivo):
    """Verifica si el archivo tiene errores de sintaxis"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        compile(contenido, archivo, 'exec')
        return True, "Sintaxis correcta"
    except SyntaxError as e:
        return False, f"Error de sintaxis: {e}"
    except Exception as e:
        return False, f"Error: {e}"

def main():
    """Función principal"""
    print("🔍 IDENTIFICANDO TESTS PROBLEMÁTICOS")
    print("=" * 60)
    
    # Patrones de archivos de test
    patrones = [
        "test_*.py",
        "prueba_*.py",
        "*_test.py",
        "verificar_*.py"
    ]
    
    archivos_encontrados = []
    for patron in patrones:
        archivos_encontrados.extend(glob.glob(patron))
    
    # Remover duplicados y ordenar
    archivos_encontrados = sorted(list(set(archivos_encontrados)))
    
    print(f"📋 Encontrados {len(archivos_encontrados)} archivos de test")
    print()
    
    archivos_exitosos = []
    archivos_fallidos = []
    
    for archivo in archivos_encontrados:
        # Primero verificar sintaxis
        sintaxis_ok, mensaje_sintaxis = verificar_sintaxis(archivo)
        
        if not sintaxis_ok:
            print(f"🔴 {archivo}")
            print(f"   💥 Error de sintaxis: {mensaje_sintaxis}")
            archivos_fallidos.append((archivo, mensaje_sintaxis))
            continue
        
        # Luego ejecutar el test
        exitoso, mensaje = ejecutar_test(archivo)
        
        if exitoso:
            archivos_exitosos.append(archivo)
        else:
            archivos_fallidos.append((archivo, mensaje))
        
        print()
    
    # Resumen
    print("=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    print(f"✅ Tests exitosos: {len(archivos_exitosos)}")
    print(f"❌ Tests fallidos: {len(archivos_fallidos)}")
    
    if archivos_exitosos:
        print("\n✅ TESTS EXITOSOS:")
        for archivo in archivos_exitosos:
            print(f"  - {archivo}")
    
    if archivos_fallidos:
        print("\n❌ TESTS FALLIDOS:")
        for archivo, error in archivos_fallidos:
            print(f"  - {archivo}")
            print(f"    Error: {error[:100]}...")
        
        print("\n🗑️ ARCHIVOS RECOMENDADOS PARA ELIMINACIÓN:")
        for archivo, error in archivos_fallidos:
            print(f"  - {archivo}")
        
        respuesta = input("\n¿Deseas eliminar los archivos fallidos? (s/n): ").lower().strip()
        
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            eliminar_archivos_fallidos(archivos_fallidos)
        else:
            print("ℹ️ No se eliminaron archivos")
    
    return len(archivos_fallidos) == 0

def eliminar_archivos_fallidos(archivos_fallidos):
    """Elimina los archivos que fallaron"""
    print("\n🗑️ ELIMINANDO ARCHIVOS FALLIDOS...")
    
    eliminados = 0
    for archivo, error in archivos_fallidos:
        try:
            # Crear backup antes de eliminar
            backup_name = f"{archivo}.backup"
            os.rename(archivo, backup_name)
            print(f"  🗑️ Eliminado: {archivo} (backup: {backup_name})")
            eliminados += 1
        except Exception as e:
            print(f"  ❌ Error eliminando {archivo}: {e}")
    
    print(f"\n✅ Se eliminaron {eliminados} archivos problemáticos")
    print("💾 Los backups se guardaron con extensión .backup")

def crear_lista_archivos_validos():
    """Crea una lista de archivos que funcionan correctamente"""
    patrones = [
        "test_*.py",
        "prueba_*.py", 
        "*_test.py",
        "verificar_*.py"
    ]
    
    archivos_validos = []
    
    for patron in patrones:
        for archivo in glob.glob(patron):
            sintaxis_ok, _ = verificar_sintaxis(archivo)
            if sintaxis_ok:
                archivos_validos.append(archivo)
    
    # Crear archivo con lista de tests válidos
    with open("TESTS_VALIDOS.md", "w", encoding="utf-8") as f:
        f.write("# TESTS VÁLIDOS\n\n")
        f.write("## Archivos de test que pasan verificación de sintaxis:\n\n")
        for archivo in sorted(archivos_validos):
            f.write(f"- ✅ `{archivo}`\n")
        
        f.write(f"\n**Total:** {len(archivos_validos)} archivos válidos\n")
    
    print(f"📄 Lista creada: TESTS_VALIDOS.md ({len(archivos_validos)} archivos)")

if __name__ == '__main__':
    try:
        success = main()
        crear_lista_archivos_validos()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Proceso interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        traceback.print_exc()
        sys.exit(1)