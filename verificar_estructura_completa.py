import os
import sys
import django
import sqlite3

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def verificar_estructura_completa():
    """Verificar todos los campos de la tabla reconocimiento_facial"""
    with connection.cursor() as cursor:
        # Obtener estructura completa de la tabla
        cursor.execute("PRAGMA table_info(reconocimiento_facial)")
        campos = cursor.fetchall()
        
        print("=" * 60)
        print("📊 ESTRUCTURA COMPLETA: reconocimiento_facial")
        print("=" * 60)
        
        campos_no_null = []
        for campo in campos:
            cid, nombre, tipo, not_null, default, pk = campo
            estado = "🔒 NOT NULL" if not_null else "✅ NULL OK"
            if default is not None:
                estado += f" (default: {default})"
            
            print(f"{nombre:<25} | {tipo:<15} | {estado}")
            
            if not_null and default is None and not pk:
                campos_no_null.append(nombre)
        
        print(f"\n🚨 CAMPOS QUE REQUIEREN VALOR (NOT NULL sin default):")
        for campo in campos_no_null:
            print(f"   - {campo}")
        
        return campos_no_null

if __name__ == '__main__':
    verificar_estructura_completa()