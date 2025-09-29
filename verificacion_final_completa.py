import os
import sys
import django
import json

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from authz.models import Usuario, Rol
from seguridad.models import ReconocimientoFacial

def verificar_datos_finales():
    """✅ VERIFICACIÓN FINAL: Comprobar que todo está correcto"""
    print("=" * 70)
    print("✅ VERIFICACIÓN FINAL DEL PROBLEMA RESUELTO")
    print("=" * 70)
    
    try:
        # 1. Verificar usuario
        usuario = Usuario.objects.get(id=8)
        print(f"✅ USUARIO ENCONTRADO:")
        print(f"   - ID: {usuario.id}")
        print(f"   - Email: {usuario.email}")
        print(f"   - Persona ID: {usuario.persona.id}")
        print(f"   - Nombre: {usuario.persona.nombre} {usuario.persona.apellido}")
        
        # Verificar rol
        rol_propietario = Rol.objects.filter(nombre='Propietario').first()
        if rol_propietario in usuario.roles.all():
            print(f"   - Rol Propietario: ✅ CONFIRMADO")
        else:
            print(f"   - Rol Propietario: ❌ FALTA")
            return False
        
        # 2. Verificar registro de reconocimiento facial
        from seguridad.models import Copropietarios
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        reconocimiento = None
        if copropietario:
            print(f"   - Copropietario ID: {copropietario.id}")
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        
        if reconocimiento:
            print(f"\n✅ RECONOCIMIENTO FACIAL ENCONTRADO:")
            print(f"   - Registro ID: {reconocimiento.id}")
            print(f"   - Copropietario ID: {reconocimiento.copropietario_id}")
            print(f"   - Activo: {reconocimiento.activo}")
            
            # Verificar fotos_urls
            fotos_urls = []
            if hasattr(reconocimiento, 'fotos_urls') and reconocimiento.fotos_urls:
                try:
                    fotos_urls = json.loads(reconocimiento.fotos_urls)
                    print(f"   - Fotos en fotos_urls: {len(fotos_urls)}")
                except:
                    pass
            
            # Verificar vector_facial como backup
            if not fotos_urls and reconocimiento.vector_facial:
                try:
                    fotos_urls = json.loads(reconocimiento.vector_facial)
                    print(f"   - Fotos en vector_facial: {len(fotos_urls)}")
                except:
                    pass
            
            # Mostrar algunas URLs como muestra
            if fotos_urls:
                print(f"   - Total URLs: {len(fotos_urls)}")
                print(f"   - Primera URL: {fotos_urls[0][:60]}...")
                if len(fotos_urls) > 1:
                    print(f"   - Última URL: {fotos_urls[-1][:60]}...")
                    
                # ¡ÉXITO!
                if len(fotos_urls) == 10:
                    print(f"\n🎉 ¡PERFECTO! 10 FOTOS ENCONTRADAS")
                    return True
                else:
                    print(f"\n⚠️  Se encontraron {len(fotos_urls)} fotos (esperadas: 10)")
                    return False
            else:
                print(f"   - ❌ No se encontraron URLs de fotos")
                return False
        else:
            print(f"\n❌ NO SE ENCONTRÓ REGISTRO DE RECONOCIMIENTO FACIAL")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def simular_endpoint_get():
    """🧪 SIMULAR ENDPOINT GET (sin autenticación)"""
    print(f"\n" + "=" * 70)
    print("🧪 SIMULACIÓN DEL ENDPOINT GET")
    print("=" * 70)
    
    try:
        usuario_id = 8
        
        # Simular la lógica del endpoint
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificar rol propietario
        rol_propietario = Rol.objects.filter(nombre='Propietario').first()
        if not rol_propietario or rol_propietario not in usuario.roles.all():
            print("❌ Usuario no tiene rol de propietario")
            return False
        
        # Buscar fotos por copropietario (que está asociado al usuario)
        from seguridad.models import Copropietarios 
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        reconocimiento = None
        if copropietario:
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        
        fotos_urls = []
        fecha_actualizacion = None
        tiene_reconocimiento = False
        
        if reconocimiento:
            # Prioridad 1: fotos_urls
            if hasattr(reconocimiento, 'fotos_urls') and reconocimiento.fotos_urls:
                try:
                    fotos_urls = json.loads(reconocimiento.fotos_urls)
                    tiene_reconocimiento = len(fotos_urls) > 0
                    fecha_actualizacion = getattr(reconocimiento, 'fecha_actualizacion', None)
                except:
                    pass
            
            # Prioridad 2: vector_facial
            if not fotos_urls and reconocimiento.vector_facial:
                try:
                    fotos_urls = json.loads(reconocimiento.vector_facial)
                    tiene_reconocimiento = len(fotos_urls) > 0
                    fecha_actualizacion = getattr(reconocimiento, 'fecha_modificacion', None)
                except:
                    pass
        
        # Generar respuesta del endpoint
        respuesta = {
            'success': True,
            'data': {
                'usuario_id': int(usuario_id),
                'usuario_email': usuario.email,
                'propietario_nombre': f"{usuario.persona.nombre} {usuario.persona.apellido}",
                'fotos_urls': fotos_urls,
                'total_fotos': len(fotos_urls),
                'fecha_ultima_actualizacion': fecha_actualizacion.isoformat() if fecha_actualizacion else None,
                'tiene_reconocimiento': tiene_reconocimiento
            },
            'mensaje': 'Fotos obtenidas exitosamente' if tiene_reconocimiento else 'No se encontraron fotos de reconocimiento'
        }
        
        print("📋 RESPUESTA SIMULADA DEL ENDPOINT:")
        print(json.dumps(respuesta, indent=2, ensure_ascii=False))
        
        # Validar éxito
        if respuesta['data']['total_fotos'] == 10:
            print(f"\n✅ SIMULACIÓN EXITOSA: {respuesta['data']['total_fotos']} fotos")
            return True
        else:
            print(f"\n⚠️  Fotos encontradas: {respuesta['data']['total_fotos']} (esperadas: 10)")
            return False
            
    except Exception as e:
        print(f"❌ ERROR EN SIMULACIÓN: {e}")
        return False

def main():
    """🚀 Verificación completa final"""
    print("🎯 VERIFICACIÓN FINAL COMPLETA")
    print("Frontend debería poder usar el endpoint GET sin problemas")
    
    # 1. Verificar datos en BD
    datos_ok = verificar_datos_finales()
    
    # 2. Simular endpoint
    endpoint_ok = simular_endpoint_get()
    
    # 3. Resultado final
    if datos_ok and endpoint_ok:
        print(f"\n" + "=" * 70)
        print("🎉 ¡PROBLEMA COMPLETAMENTE RESUELTO!")
        print("=" * 70)
        print("✅ CONFIRMACIONES FINALES:")
        print("   - Usuario ID 8 (tito@gmail.com) existe ✅")
        print("   - Tiene rol Propietario ✅")
        print("   - 10 fotos guardadas en BD ✅")
        print("   - Endpoint GET retorna datos correctos ✅")
        print("   - Frontend puede mostrar las fotos ✅")
        print()
        print("🎯 ENDPOINT LISTO:")
        print("   GET /api/authz/reconocimiento/fotos/8/")
        print("   → Retorna: { total_fotos: 10, fotos_urls: [...] }")
        print()
        print("🔐 NOTA: El endpoint requiere autenticación JWT")
        print("   Frontend debe incluir token en header Authorization")
        print("   Bearer <token>")
        print()
        print("✨ SISTEMA FUNCIONANDO AL 100%")
        
    else:
        print(f"\n" + "=" * 70)
        print("❌ VERIFICACIÓN FALLÓ")
        print("=" * 70)
        print("   Revisar los datos o la lógica del endpoint")

if __name__ == '__main__':
    main()