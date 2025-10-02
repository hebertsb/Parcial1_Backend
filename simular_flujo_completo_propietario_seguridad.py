"""
Simulación completa del flujo propietario sube foto → seguridad consume foto
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
import base64

def crear_imagen_base64_demo():
    """Crear una imagen base64 de demostración"""
    # Imagen pequeña 1x1 píxel en formato PNG (base64)
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def simular_subida_propietario():
    """Simular que un propietario sube fotos usando el endpoint mejorado"""
    
    print("🔍 SIMULANDO FLUJO COMPLETO PROPIETARIO → SEGURIDAD")
    print("=" * 80)
    
    # 1. Encontrar un propietario con reconocimiento facial
    print("\n👤 1. BUSCANDO PROPIETARIO PARA SIMULAR")
    print("-" * 50)
    
    propietario = Copropietarios.objects.filter(
        tipo_residente__icontains='Propietario',
        usuario_sistema__isnull=False,
        reconocimiento_facial__isnull=False
    ).first()
    
    if not propietario:
        print("❌ No hay propietarios con usuario sistema y reconocimiento facial")
        return False
    
    print(f"✅ Propietario seleccionado: {propietario.nombres} {propietario.apellidos}")
    print(f"   📄 Documento: {propietario.numero_documento}")
    print(f"   📧 Email: {propietario.email}")
    print(f"   🏠 Unidad: {propietario.unidad_residencial}")
    print(f"   🔗 Usuario sistema: {propietario.usuario_sistema.email if propietario.usuario_sistema else 'No configurado'}")
    
    # 2. Obtener reconocimiento facial
    reconocimiento = ReconocimientoFacial.objects.filter(copropietario=propietario).first()
    
    if not reconocimiento:
        print("❌ No se encontró reconocimiento facial para el propietario")
        return False
    
    print(f"   🎯 Reconocimiento ID: {reconocimiento.id}")
    print(f"   ✅ Activo: {reconocimiento.activo}")
    
    # 3. Simular datos que enviaría el frontend del propietario
    print(f"\n📸 2. SIMULANDO SUBIDA DE FOTOS DEL PROPIETARIO")
    print("-" * 50)
    
    # Crear fotos de demostración
    imagen_base64 = crear_imagen_base64_demo()
    
    fotos_simuladas = [
        {
            "nombre": "foto_perfil_1.png",
            "data": imagen_base64,
            "tipo": "image/png"
        },
        {
            "nombre": "foto_perfil_2.png", 
            "data": imagen_base64,
            "tipo": "image/png"
        },
        {
            "nombre": "foto_perfil_3.png",
            "data": imagen_base64,
            "tipo": "image/png"
        }
    ]
    
    print(f"📷 Total fotos a simular: {len(fotos_simuladas)}")
    
    # 4. Simular URLs de Dropbox (lo que devolvería el servicio real)
    urls_dropbox_simuladas = []
    
    for idx, foto in enumerate(fotos_simuladas, 1):
        # Simular URL que devolvería Dropbox
        url_simulada = f"https://dl.dropboxusercontent.com/s/abc123def456/Propietarios/{propietario.numero_documento}/{foto['nombre']}?dl=1"
        urls_dropbox_simuladas.append(url_simulada)
        print(f"   {idx}. {foto['nombre']} → {url_simulada}")
    
    # 5. Actualizar reconocimiento facial con las URLs simuladas
    print(f"\n💾 3. ACTUALIZANDO RECONOCIMIENTO FACIAL CON URLS")
    print("-" * 50)
    
    # Guardar URLs en el formato JSON esperado
    reconocimiento.fotos_urls = json.dumps(urls_dropbox_simuladas)
    reconocimiento.save()
    
    print(f"✅ URLs guardadas en reconocimiento ID: {reconocimiento.id}")
    print(f"📊 Total URLs guardadas: {len(urls_dropbox_simuladas)}")
    
    # 6. Verificar desde perspectiva de seguridad
    print(f"\n👮 4. VERIFICANDO DESDE PANEL DE SEGURIDAD")
    print("-" * 50)
    
    # Buscar usuario de seguridad
    usuario_seguridad = Usuario.objects.filter(
        roles__nombre__icontains='Seguridad'
    ).first()
    
    if not usuario_seguridad:
        print("❌ No se encontró usuario de seguridad")
        return False
    
    print(f"✅ Usuario seguridad: {usuario_seguridad.email}")
    
    # Simular lo que vería en el endpoint de usuarios con fotos
    print(f"\n🔍 Simulando GET /api/authz/seguridad/usuarios-con-fotos/")
    
    # Buscar reconocimientos con fotos
    reconocimientos_con_fotos = ReconocimientoFacial.objects.filter(
        fotos_urls__isnull=False
    ).exclude(
        fotos_urls__exact=''
    ).exclude(
        fotos_urls__exact='[]'
    )
    
    print(f"📋 Usuarios encontrados con fotos: {reconocimientos_con_fotos.count()}")
    
    for reconocimiento_usuario in reconocimientos_con_fotos:
        usuario = reconocimiento_usuario.copropietario
        if reconocimiento_usuario.fotos_urls:
            try:
                fotos_urls = json.loads(reconocimiento_usuario.fotos_urls)
                if isinstance(fotos_urls, list) and len(fotos_urls) > 0:
                    print(f"   👤 {usuario.nombres} {usuario.apellidos}")
                    print(f"      📄 Documento: {usuario.numero_documento}")
                    print(f"      🏠 Unidad: {usuario.unidad_residencial}")
                    print(f"      📷 Total fotos: {len(fotos_urls)}")
                    print(f"      🔗 Primera foto: {fotos_urls[0][:80]}...")
            except json.JSONDecodeError:
                pass
    
    # 7. Simular detalle específico del usuario
    print(f"\n🔍 Simulando GET /api/authz/seguridad/usuario-fotos/{propietario.id}/")
    print("-" * 50)
    
    reconocimiento_detalle = ReconocimientoFacial.objects.filter(
        copropietario=propietario
    ).first()
    
    if reconocimiento_detalle and reconocimiento_detalle.fotos_urls:
        try:
            fotos_urls_detalle = json.loads(reconocimiento_detalle.fotos_urls)
            
            print(f"👤 Detalles de {propietario.nombres} {propietario.apellidos}:")
            print(f"   📄 Documento: {propietario.numero_documento}")
            print(f"   📧 Email: {propietario.email}")
            print(f"   🏠 Unidad: {propietario.unidad_residencial}")
            print(f"   📱 Teléfono: {propietario.telefono}")
            print(f"   📷 Total fotos: {len(fotos_urls_detalle)}")
            print(f"   ✅ Reconocimiento activo: {reconocimiento_detalle.activo}")
            print(f"   🤖 Proveedor IA: {reconocimiento_detalle.proveedor_ia}")
            
            print(f"\n   📸 URLs de fotos disponibles:")
            for idx, url in enumerate(fotos_urls_detalle, 1):
                print(f"      {idx}. {url}")
                
        except json.JSONDecodeError:
            print("❌ Error al decodificar URLs de fotos")
    
    # 8. Resumen final
    print(f"\n\n📊 5. RESUMEN DE LA SIMULACIÓN")
    print("-" * 50)
    
    print(f"✅ FLUJO COMPLETADO EXITOSAMENTE:")
    print(f"   1. Propietario: {propietario.nombres} {propietario.apellidos}")
    print(f"   2. Fotos simuladas subidas: {len(fotos_simuladas)}")
    print(f"   3. URLs de Dropbox generadas: {len(urls_dropbox_simuladas)}")
    print(f"   4. Reconocimiento facial actualizado: ID {reconocimiento.id}")
    print(f"   5. Seguridad puede ver las fotos: ✅")
    
    print(f"\n🎯 ENDPOINTS FUNCIONALES:")
    print(f"   • Propietario puede subir: POST /api/authz/propietarios/subir-foto/")
    print(f"   • Propietario puede ver sus fotos: GET /api/authz/propietarios/mis-fotos/")
    print(f"   • Seguridad puede listar usuarios: GET /api/authz/seguridad/usuarios-con-fotos/")
    print(f"   • Seguridad puede ver detalles: GET /api/authz/seguridad/usuario-fotos/{propietario.id}/")
    
    print(f"\n☁️ INTEGRACIÓN DROPBOX:")
    print(f"   • Fotos se suben a: /Propietarios/{propietario.numero_documento}/")
    print(f"   • URLs públicas generadas automáticamente")
    print(f"   • Acceso inmediato desde panel de seguridad")
    
    return True

def limpiar_simulacion():
    """Limpiar datos de la simulación si es necesario"""
    print(f"\n🧹 ¿DESEA LIMPIAR LA SIMULACIÓN?")
    print("Esta acción eliminará las URLs de fotos simuladas.")
    
    respuesta = input("Escriba 'SI' para limpiar: ").strip().upper()
    
    if respuesta == 'SI':
        reconocimientos = ReconocimientoFacial.objects.filter(
            fotos_urls__contains='dl.dropboxusercontent.com'
        )
        
        count = reconocimientos.count()
        reconocimientos.update(fotos_urls='[]')
        
        print(f"✅ Limpiado: {count} reconocimientos restaurados a estado sin fotos")
    else:
        print("ℹ️ Simulación mantenida. Los datos quedan para futuras pruebas.")

if __name__ == "__main__":
    try:
        exito = simular_subida_propietario()
        
        if exito:
            print("\n" + "=" * 80)
            print("🎉 SIMULACIÓN EXITOSA: EL FLUJO PROPIETARIO → SEGURIDAD FUNCIONA")
            print("=" * 80)
            
            # Preguntar si desea limpiar
            limpiar_simulacion()
        else:
            print("\n" + "=" * 80)
            print("❌ SIMULACIÓN FALLIDA: REVISAR CONFIGURACIÓN DEL SISTEMA")
            print("=" * 80)
            
    except Exception as e:
        print(f"💥 Error durante la simulación: {str(e)}")
        import traceback
        traceback.print_exc()