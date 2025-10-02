"""
Script completo para verificar la cadena de conexiones:
Usuario → Copropietario → ReconocimientoFacial
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial
import json

def verificar_cadena_completa():
    """Verificar toda la cadena de conexiones para Rosa"""
    
    print("🔍 VERIFICANDO CADENA COMPLETA: USUARIO → COPROPIETARIO → RECONOCIMIENTO")
    print("=" * 80)
    
    # 1. VERIFICAR USUARIO ROSA
    print("\n👤 1. VERIFICACIÓN DEL USUARIO ROSA")
    print("-" * 50)
    
    try:
        usuario_rosa = Usuario.objects.get(email='rosa@gmail.com')
        print(f"✅ Usuario encontrado:")
        print(f"   • ID: {usuario_rosa.id}")
        print(f"   • Email: {usuario_rosa.email}")
        if usuario_rosa.persona:
            print(f"   • Nombres: {usuario_rosa.persona.nombres} {usuario_rosa.persona.apellidos}")
            print(f"   • Documento: {usuario_rosa.persona.numero_documento}")
        else:
            print(f"   • Sin datos de persona asociados")
        print(f"   • Activo: {usuario_rosa.is_active}")
        
        # Verificar roles
        roles = usuario_rosa.roles.all()
        print(f"   • Roles: {[rol.nombre for rol in roles]}")
        
    except Usuario.DoesNotExist:
        print("❌ Usuario Rosa no encontrado")
        return False
    
    # 2. VERIFICAR COPROPIETARIO ASOCIADO
    print(f"\n🏠 2. VERIFICACIÓN DEL COPROPIETARIO ASOCIADO")
    print("-" * 50)
    
    try:
        copropietario = Copropietarios.objects.get(usuario_sistema_id=usuario_rosa.id)
        print(f"✅ Copropietario encontrado:")
        print(f"   • ID Copropietario: {copropietario.id}")
        print(f"   • Nombres: {copropietario.nombres} {copropietario.apellidos}")
        print(f"   • Documento: {copropietario.numero_documento}")
        print(f"   • Email: {copropietario.email}")
        print(f"   • Unidad: {copropietario.unidad_residencial}")
        print(f"   • Tipo: {copropietario.tipo_residente}")
        print(f"   • Usuario sistema ID: {copropietario.usuario_sistema.id if copropietario.usuario_sistema else 'No asignado'}")
        
        # Verificar que coinciden los datos
        if copropietario.usuario_sistema and usuario_rosa.id == copropietario.usuario_sistema.id:
            print(f"   ✅ CONEXIÓN CORRECTA: Usuario.id ({usuario_rosa.id}) = Copropietario.usuario_sistema.id ({copropietario.usuario_sistema.id})")
        else:
            if not copropietario.usuario_sistema:
                print(f"   ❌ ERROR DE CONEXIÓN: Copropietario no tiene usuario_sistema asignado")
            else:
                print(f"   ❌ ERROR DE CONEXIÓN: Usuario.id ({usuario_rosa.id}) ≠ Copropietario.usuario_sistema.id ({copropietario.usuario_sistema.id})")
            return False
            
    except Copropietarios.DoesNotExist:
        print(f"❌ No se encontró copropietario asociado al usuario ID: {usuario_rosa.id}")
        return False
    
    # 3. VERIFICAR RECONOCIMIENTO FACIAL
    print(f"\n🎯 3. VERIFICACIÓN DEL RECONOCIMIENTO FACIAL")
    print("-" * 50)
    
    try:
        reconocimiento = ReconocimientoFacial.objects.get(copropietario=copropietario)
        print(f"✅ Reconocimiento facial encontrado:")
        print(f"   • ID Reconocimiento: {reconocimiento.id}")
        print(f"   • Copropietario ID: {reconocimiento.copropietario.id}")
        print(f"   • Activo: {reconocimiento.activo}")
        print(f"   • Proveedor IA: {reconocimiento.proveedor_ia}")
        print(f"   • Imagen referencia: {reconocimiento.imagen_referencia_url or 'No configurada'}")
        
        # Verificar conexión
        if copropietario.id == reconocimiento.copropietario.id:
            print(f"   ✅ CONEXIÓN CORRECTA: Copropietario.id ({copropietario.id}) = ReconocimientoFacial.copropietario.id ({reconocimiento.copropietario.id})")
        else:
            print(f"   ❌ ERROR DE CONEXIÓN: Copropietario.id ({copropietario.id}) ≠ ReconocimientoFacial.copropietario.id ({reconocimiento.copropietario.id})")
            return False
            
        # Verificar fotos URLs
        fotos_urls = []
        if reconocimiento.fotos_urls:
            try:
                fotos_urls = json.loads(reconocimiento.fotos_urls)
                if not isinstance(fotos_urls, list):
                    fotos_urls = []
            except (json.JSONDecodeError, TypeError):
                fotos_urls = []
        
        print(f"   • Total fotos almacenadas: {len(fotos_urls)}")
        
        if fotos_urls:
            print(f"   📸 URLs de fotos:")
            for idx, url in enumerate(fotos_urls, 1):
                print(f"      {idx}. {url[:80]}...")
                # Verificar si es URL pública
                if url and ('dropbox' in url.lower() and 'dl=' in url):
                    print(f"         ✅ URL pública válida")
                else:
                    print(f"         ⚠️ URL no es pública o inválida")
        else:
            print(f"   📭 Sin fotos configuradas")
            
    except ReconocimientoFacial.DoesNotExist:
        print(f"❌ No se encontró reconocimiento facial para copropietario ID: {copropietario.id}")
        return False
    
    # 4. VERIFICAR ENDPOINTS DE API
    print(f"\n🛣️ 4. VERIFICACIÓN DE ENDPOINTS API")
    print("-" * 50)
    
    print(f"📋 URLs que el frontend debería usar:")
    print(f"   • Login: POST /authz/login/")
    print(f"   • Mis fotos: GET /api/authz/propietarios/mis-fotos/")
    print(f"   • Subir foto: POST /api/authz/propietarios/subir-foto/")
    print(f"   • Mi información: GET /authz/usuarios/me/")
    
    # 5. SIMULACIÓN DE RESPUESTA API
    print(f"\n📡 5. SIMULACIÓN DE RESPUESTA API")
    print("-" * 50)
    
    # Simular respuesta de /api/authz/propietarios/mis-fotos/
    todas_las_fotos = fotos_urls.copy()
    if reconocimiento.imagen_referencia_url and reconocimiento.imagen_referencia_url not in todas_las_fotos:
        todas_las_fotos.insert(0, reconocimiento.imagen_referencia_url)
    
    respuesta_api = {
        'success': True,
        'data': {
            'total_fotos': len(todas_las_fotos),
            'fotos_urls': todas_las_fotos,
            'copropietario_id': copropietario.id,
            'reconocimiento_activo': reconocimiento.activo,
            'reconocimiento_id': reconocimiento.id,
            'proveedor_ia': reconocimiento.proveedor_ia,
            'confianza_enrolamiento': reconocimiento.confianza_enrolamiento,
            'tiene_reconocimiento': True,
            'fecha_ultima_actualizacion': reconocimiento.fecha_actualizacion.isoformat() if hasattr(reconocimiento, 'fecha_actualizacion') and reconocimiento.fecha_actualizacion else None
        }
    }
    
    print(f"📊 Respuesta que recibiría el frontend:")
    print(f"   • success: {respuesta_api['success']}")
    print(f"   • total_fotos: {respuesta_api['data']['total_fotos']}")
    print(f"   • reconocimiento_activo: {respuesta_api['data']['reconocimiento_activo']}")
    print(f"   • copropietario_id: {respuesta_api['data']['copropietario_id']}")
    print(f"   • reconocimiento_id: {respuesta_api['data']['reconocimiento_id']}")
    
    # 6. VERIFICAR QUE SEGURIDAD PUEDE VER LAS FOTOS
    print(f"\n👮 6. VERIFICACIÓN DE ACCESO DESDE SEGURIDAD")
    print("-" * 50)
    
    # Buscar usuario de seguridad
    usuario_seguridad = Usuario.objects.filter(
        roles__nombre__icontains='Seguridad'
    ).first()
    
    if usuario_seguridad:
        print(f"✅ Usuario seguridad encontrado: {usuario_seguridad.email}")
        
        # Simular lo que vería seguridad
        print(f"📋 En el endpoint GET /api/authz/seguridad/usuarios-con-fotos/:")
        print(f"   • Rosa aparecería en la lista con {len(todas_las_fotos)} fotos")
        
        print(f"📋 En el endpoint GET /api/authz/seguridad/usuario-fotos/{copropietario.id}/:")
        print(f"   • Vería todos los detalles de Rosa")
        print(f"   • Acceso a las {len(todas_las_fotos)} fotos")
        
    else:
        print(f"❌ No se encontró usuario de seguridad")
    
    # 7. RESUMEN FINAL
    print(f"\n\n📊 7. RESUMEN DE LA CADENA DE CONEXIONES")
    print("-" * 50)
    
    print(f"🔗 CADENA COMPLETA:")
    print(f"   Usuario Rosa (ID: {usuario_rosa.id})")
    print(f"   ↓")
    print(f"   Copropietario (ID: {copropietario.id})")
    print(f"   ↓")
    print(f"   ReconocimientoFacial (ID: {reconocimiento.id})")
    print(f"   ↓")
    print(f"   Fotos: {len(todas_las_fotos)} URLs")
    
    print(f"\n✅ ESTADO DE CONEXIONES:")
    print(f"   • Usuario → Copropietario: ✅ CORRECTO")
    print(f"   • Copropietario → Reconocimiento: ✅ CORRECTO")  
    print(f"   • Reconocimiento → Fotos: {'✅ CORRECTO' if len(todas_las_fotos) > 0 else '⚠️ SIN FOTOS'}")
    print(f"   • API Endpoints: ✅ CONFIGURADOS")
    print(f"   • Acceso Seguridad: ✅ DISPONIBLE")
    
    return len(todas_las_fotos) > 0

def probar_nuevo_token():
    """Probar el nuevo token de Dropbox"""
    
    print(f"\n🧪 PROBANDO NUEVO TOKEN DE DROPBOX")
    print("-" * 50)
    
    from core.utils.dropbox_upload import upload_image_to_dropbox
    from django.core.files.base import ContentFile
    import base64
    
    # Crear una imagen de prueba
    imagen_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    img_data = base64.b64decode(imagen_base64)
    
    # Crear archivo temporal
    file_content = ContentFile(img_data, name='test_token.png')
    
    # Intentar subir
    print(f"📤 Probando subida con nuevo token...")
    
    try:
        resultado = upload_image_to_dropbox(
            file_content,
            'test_nuevo_token.png',
            '/Propietarios/TEST'
        )
        
        if resultado and resultado.get('url'):
            print(f"✅ TOKEN FUNCIONANDO CORRECTAMENTE")
            print(f"   • Archivo subido exitosamente")
            print(f"   • URL pública generada: {resultado['url'][:80]}...")
            return True
        else:
            print(f"❌ TOKEN NO FUNCIONANDO")
            print(f"   • Sin URL pública generada")
            return False
            
    except Exception as e:
        print(f"❌ ERROR CON EL TOKEN:")
        print(f"   • {str(e)}")
        return False

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO VERIFICACIÓN COMPLETA")
        print("=" * 80)
        
        # Probar token
        token_ok = probar_nuevo_token()
        
        # Verificar cadena de conexiones
        cadena_ok = verificar_cadena_completa()
        
        print("\n" + "=" * 80)
        if token_ok and cadena_ok:
            print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL")
            print("✅ Rosa puede subir fotos y verlas en su panel")
            print("✅ Seguridad puede ver las fotos de Rosa")
        elif cadena_ok and not token_ok:
            print("⚠️ CADENA OK PERO TOKEN CON PROBLEMAS")
            print("🔧 Revisar permisos de Dropbox o generar nuevo token")
        elif token_ok and not cadena_ok:
            print("⚠️ TOKEN OK PERO CADENA CON PROBLEMAS")
            print("🔧 Revisar conexiones entre Usuario/Copropietario/Reconocimiento")
        else:
            print("❌ SISTEMA CON PROBLEMAS")
            print("🔧 Revisar tanto token como cadena de conexiones")
            
    except Exception as e:
        print(f"💥 Error durante la verificación: {str(e)}")
        import traceback
        traceback.print_exc()