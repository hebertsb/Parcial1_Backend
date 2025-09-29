# 🔍 DIAGNÓSTICO COMPLETO: BACKEND NO ENCUENTRA FOTOS

import os
import sys
import django
import json

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from seguridad.models import ReconocimientoFacial

def diagnosticar_usuario_8():
    """🔍 Diagnóstico específico del usuario ID 8"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO: USUARIO ID 8 - tito@gmail.com")
    print("=" * 60)
    
    # 1. Verificar usuario existe y tiene rol propietario
    try:
        usuario = Usuario.objects.get(id=8)
        print(f"✅ Usuario encontrado: {usuario.email}")
        
        # Verificar rol propietario
        rol_propietario = Rol.objects.filter(nombre='Propietario').first()
        if rol_propietario in usuario.roles.all():
            print("✅ Tiene rol Propietario")
        else:
            print("❌ NO tiene rol Propietario")
            return
        
        # Verificar persona asociada
        if usuario.persona:
            print(f"✅ Persona asociada: ID {usuario.persona.id} - {usuario.persona.nombre} {usuario.persona.apellido}")
            persona_id = usuario.persona.id
        else:
            print("❌ NO tiene persona asociada")
            return
            
    except Usuario.DoesNotExist:
        print("❌ Usuario ID 8 no encontrado")
        return
    except Exception as e:
        print(f"❌ Error verificando usuario: {e}")
        return
    
    # 2. Buscar registro de reconocimiento facial
    print(f"\n🔍 BUSCANDO REGISTRO DE RECONOCIMIENTO FACIAL:")
    print(f"   - Buscando por persona_id: {persona_id}")
    
    try:
        # Buscar por persona_id (como hace el endpoint corregido)
        registros_persona = ReconocimientoFacial.objects.filter(persona_id=persona_id)
        print(f"   - Registros por persona_id: {registros_persona.count()}")
        
        # Buscar por copropietario (modelo original)
        from seguridad.models import Copropietarios
        try:
            copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
            if copropietario:
                registros_copropietario = ReconocimientoFacial.objects.filter(copropietario=copropietario)
                print(f"   - Registros por copropietario: {registros_copropietario.count()}")
            else:
                print("   - No tiene registro en Copropietarios")
        except Exception as e:
            print(f"   - Error buscando copropietario: {e}")
        
        # Buscar todos los registros para debug
        todos_registros = ReconocimientoFacial.objects.all()
        print(f"   - Total registros en tabla: {todos_registros.count()}")
        
    except Exception as e:
        print(f"❌ Error buscando registros: {e}")
        return
    
    # 3. Analizar registros encontrados
    print(f"\n📊 ANÁLISIS DE REGISTROS:")
    
    for i, registro in enumerate(registros_persona):
        print(f"\n   📋 Registro {i+1} (ID: {registro.id}):")
        print(f"      - persona_id: {getattr(registro, 'persona_id', 'N/A')}")
        print(f"      - copropietario: {getattr(registro, 'copropietario', 'N/A')}")
        
        # Verificar campo fotos_urls
        if hasattr(registro, 'fotos_urls'):
            fotos_urls = getattr(registro, 'fotos_urls', None)
            print(f"      - fotos_urls existe: {fotos_urls is not None}")
            
            if fotos_urls:
                print(f"      - fotos_urls contenido: {type(fotos_urls)} - {len(str(fotos_urls))} caracteres")
                try:
                    if isinstance(fotos_urls, str):
                        urls = json.loads(fotos_urls)
                        print(f"      - URLs parseadas: {len(urls)} fotos")
                        for j, url in enumerate(urls[:2]):
                            print(f"        * URL {j+1}: {url[:60]}...")
                    else:
                        print(f"      - fotos_urls no es string: {fotos_urls}")
                except json.JSONDecodeError as e:
                    print(f"      - ERROR parseando JSON: {e}")
                    print(f"      - Contenido raw: {fotos_urls[:100]}...")
            else:
                print("      - fotos_urls está vacío")
        else:
            print("      - Campo fotos_urls NO existe")
        
        # Verificar otros campos relevantes
        if hasattr(registro, 'imagen_referencia_url'):
            img_url = getattr(registro, 'imagen_referencia_url', None)
            if img_url:
                print(f"      - imagen_referencia_url: {img_url[:60]}...")
            else:
                print("      - imagen_referencia_url: vacío")
        
        # Verificar fechas
        if hasattr(registro, 'fecha_actualizacion'):
            fecha = getattr(registro, 'fecha_actualizacion', None)
            print(f"      - fecha_actualizacion: {fecha}")
        
        if hasattr(registro, 'fecha_modificacion'):
            fecha = getattr(registro, 'fecha_modificacion', None)
            print(f"      - fecha_modificacion: {fecha}")

def verificar_estructura_tabla():
    """🔧 Verificar estructura de la tabla ReconocimientoFacial"""
    print(f"\n" + "=" * 60)
    print("🔧 VERIFICACIÓN DE ESTRUCTURA DE TABLA")
    print("=" * 60)
    
    try:
        # Obtener todos los campos del modelo
        campos = [field.name for field in ReconocimientoFacial._meta.fields]
        print(f"✅ Campos disponibles: {campos}")
        
        # Verificar campos específicos que necesitamos
        campos_necesarios = ['persona_id', 'fotos_urls', 'fecha_actualizacion']
        for campo in campos_necesarios:
            if campo in campos:
                print(f"   ✅ {campo}: Disponible")
            else:
                print(f"   ❌ {campo}: NO disponible")
        
    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")

def probar_endpoint_directo():
    """🧪 Probar endpoint GET directamente"""
    print(f"\n" + "=" * 60)
    print("🧪 PRUEBA DIRECTA DEL ENDPOINT GET")
    print("=" * 60)
    
    try:
        from authz.views_fotos_reconocimiento_corregido import obtener_fotos_reconocimiento_corregido
        from django.test import RequestFactory
        
        # Crear request simulado
        factory = RequestFactory()
        request = factory.get('/api/authz/reconocimiento/fotos/8/')
        
        # Simular usuario autenticado
        usuario = Usuario.objects.get(id=8)
        request.user = usuario
        
        print(f"🎯 Probando endpoint con usuario ID 8...")
        
        # Llamar al endpoint
        response = obtener_fotos_reconocimiento_corregido(request, 8)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📊 Response Data: {json.dumps(response.data, indent=2, default=str)}")
        
        if response.status_code == 200:
            data = response.data.get('data', {})
            total_fotos = data.get('total_fotos', 0)
            if total_fotos > 0:
                print(f"✅ ¡FOTOS ENCONTRADAS! Total: {total_fotos}")
            else:
                print(f"❌ NO se encontraron fotos (total_fotos: {total_fotos})")
        else:
            print(f"❌ Error en endpoint: {response.data}")
            
    except Exception as e:
        print(f"❌ Error probando endpoint: {e}")
        import traceback
        traceback.print_exc()

def main():
    """🚀 Ejecutar diagnóstico completo"""
    diagnosticar_usuario_8()
    verificar_estructura_tabla()
    probar_endpoint_directo()
    
    print(f"\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    print("1. ¿El usuario ID 8 existe y tiene rol Propietario?")
    print("2. ¿Tiene persona asociada con ID válido?")
    print("3. ¿Existe registro en ReconocimientoFacial?")
    print("4. ¿El campo fotos_urls contiene las URLs de Dropbox?")
    print("5. ¿El endpoint puede parsear el JSON correctamente?")
    print("\n🔧 Con esta información podremos identificar el problema exacto")

if __name__ == '__main__':
    main()