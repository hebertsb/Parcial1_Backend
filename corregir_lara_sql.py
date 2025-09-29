# 🔧 CORRECCIÓN SQL DIRECTA: lara@gmail.com

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.utils import timezone

def crear_reconocimiento_sql():
    """
    🎯 Crear ReconocimientoFacial usando SQL directo
    """
    print('🔧 CORRECCIÓN SQL DIRECTA para lara@gmail.com')
    print('=' * 50)
    
    try:
        with connection.cursor() as cursor:
            # 1. Verificar estructura de la tabla
            cursor.execute("PRAGMA table_info(reconocimiento_facial)")
            campos = cursor.fetchall()
            
            print('📋 CAMPOS DE LA TABLA reconocimiento_facial:')
            campos_obligatorios = []
            for campo in campos:
                col_name = campo[1]
                not_null = campo[3]  # 1 si es NOT NULL
                default_value = campo[4]
                
                print(f'   - {col_name:25} | NOT NULL: {bool(not_null):5} | Default: {default_value}')
                
                if not_null and default_value is None and col_name != 'id':
                    campos_obligatorios.append(col_name)
            
            print(f'\n🔍 CAMPOS OBLIGATORIOS: {campos_obligatorios}')
            
            # 2. Verificar si ya existe
            cursor.execute("SELECT id FROM reconocimiento_facial WHERE copropietario_id = 12")
            existe = cursor.fetchone()
            
            if existe:
                print(f'⚠️  Ya existe ReconocimientoFacial con copropietario_id=12: ID {existe[0]}')
                return False
            
            # 3. Crear registro con todos los campos necesarios
            fecha_actual = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # SQL con valores literales para evitar problemas de parámetros
            sql = f"""
            INSERT INTO reconocimiento_facial (
                copropietario_id, 
                proveedor_ia, 
                vector_facial, 
                activo, 
                fecha_enrolamiento, 
                fecha_modificacion, 
                fecha_actualizacion,
                intentos_verificacion
            ) VALUES (
                12, 
                'Local', 
                '[]', 
                1, 
                '{fecha_actual}', 
                '{fecha_actual}', 
                '{fecha_actual}',
                0
            )
            """
            
            cursor.execute(sql)
            
            cursor.execute(sql)
            
            # Obtener ID del registro creado
            reconocimiento_id = cursor.lastrowid
            
            print(f'✅ ReconocimientoFacial creado exitosamente')
            print(f'   - ID: {reconocimiento_id}')
            print(f'   - Copropietario ID: 12')
            print(f'   - Vector facial: [] (vacío)')
            print(f'   - Fecha: {fecha_actual}')
            
            return True
            
    except Exception as e:
        print(f'❌ Error en creación SQL: {e}')
        
        # Mostrar campos faltantes si es un error de constraint
        if 'NOT NULL constraint failed' in str(e):
            campo_faltante = str(e).split(':')[-1].strip()
            print(f'   🔍 Campo faltante: {campo_faltante}')
        
        return False

def verificar_creacion():
    """
    ✅ Verificar que se creó correctamente
    """
    print(f'\n✅ VERIFICACIÓN FINAL')
    print('=' * 25)
    
    try:
        from seguridad.models import ReconocimientoFacial, Copropietarios
        from authz.models import Usuario
        
        # Verificar cadena completa
        usuario = Usuario.objects.get(email='lara@gmail.com')
        copropietario = Copropietarios.objects.get(id=12)
        reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=12).first()
        
        print(f'👤 Usuario: {usuario.email} (ID: {usuario.id})')
        print(f'🏠 Copropietario: {copropietario.nombres} {copropietario.apellidos} (ID: {copropietario.id})')
        print(f'📸 ReconocimientoFacial: {"✅ ID " + str(reconocimiento.id) if reconocimiento else "❌ FALTA"}')
        
        if reconocimiento:
            print(f'\n🎉 ¡CORRECCIÓN EXITOSA!')
            print(f'   - lara@gmail.com ahora puede subir fotos')
            print(f'   - Aparecerá en el panel de seguridad')
            print(f'   - Sistema de reconocimiento facial habilitado')
            return True
        else:
            print(f'\n❌ Corrección falló')
            return False
            
    except Exception as e:
        print(f'❌ Error en verificación: {e}')
        return False

if __name__ == "__main__":
    exito = crear_reconocimiento_sql()
    
    if exito:
        verificar_creacion()
    else:
        print(f'\n❌ La corrección SQL falló')