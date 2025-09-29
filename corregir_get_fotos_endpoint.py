# 🔧 CORRECCIÓN CRÍTICA: ENDPOINT GET FOTOS

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import ReconocimientoFacial, Copropietarios
import json

def corregir_endpoint_get_fotos():
    """
    🎯 OBJETIVO: Corregir la función obtener_fotos_reconocimiento_corregido
    
    PROBLEMA IDENTIFICADO:
    - El endpoint busca campo 'fotos_urls' que NO EXISTE
    - Los datos están en 'vector_facial' pero la lógica falla
    - hasattr(reconocimiento, 'fotos_urls') siempre es False
    """
    
    print("🔧 CORRECCIÓN DEL ENDPOINT GET FOTOS")
    print("=" * 50)
    
    # 1. Verificar el problema actual
    print("1. 🔍 VERIFICANDO PROBLEMA ACTUAL:")
    
    usuario = Usuario.objects.get(id=8)
    copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
    reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
    
    print(f"   - Usuario: {usuario.email}")
    print(f"   - Copropietario ID: {copropietario.id}")
    print(f"   - ReconocimientoFacial ID: {reconocimiento.id}")
    
    # 2. Probar la lógica actual (FALLIDA)
    print("\n2. 🧪 PROBANDO LÓGICA ACTUAL (FALLIDA):")
    
    fotos_urls_actual = []
    
    # Lógica actual del endpoint
    if hasattr(reconocimiento, 'fotos_urls') and reconocimiento.fotos_urls:
        print("   ❌ Buscando en 'fotos_urls' - Campo NO EXISTE")
    else:
        print("   ⚠️  Campo 'fotos_urls' no encontrado o vacío")
    
    if not fotos_urls_actual and reconocimiento.vector_facial:
        print("   ✅ Intentando leer 'vector_facial'...")
        try:
            fotos_urls_actual = json.loads(reconocimiento.vector_facial)
            print(f"   ✅ SUCCESS: {len(fotos_urls_actual)} URLs encontradas")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"   ❌ Error parseando vector_facial: {e}")
    
    # 3. Lógica CORREGIDA
    print("\n3. ✅ LÓGICA CORREGIDA:")
    
    fotos_urls_corregida = []
    
    # CORRECCIÓN: Solo buscar en vector_facial (donde están los datos)
    if reconocimiento.vector_facial:
        try:
            fotos_urls_corregida = json.loads(reconocimiento.vector_facial)
            print(f"   ✅ URLs encontradas en vector_facial: {len(fotos_urls_corregida)}")
            for i, url in enumerate(fotos_urls_corregida[:3]):
                print(f"      - Foto {i+1}: {url}")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"   ❌ Error: {e}")
    
    return fotos_urls_corregida

def generar_version_corregida():
    """
    📝 Generar la versión corregida de la función del endpoint
    """
    
    codigo_corregido = '''
def obtener_fotos_reconocimiento_corregido(request, usuario_id):
    """
    CORREGIDO: Endpoint para obtener fotos de reconocimiento facial del usuario
    URL: GET /api/authz/reconocimiento/fotos/{usuario_id}/
    """
    try:
        # 1. Validar usuario y permisos (código existente...)
        usuario = Usuario.objects.get(id=usuario_id)
        
        # Verificar rol propietario
        rol_propietario = Rol.objects.filter(nombre='Propietario').first()
        if not rol_propietario or rol_propietario not in usuario.roles.all():
            return Response({
                'success': False,
                'error': 'El usuario no tiene rol de propietario'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 2. Buscar fotos en la base de datos
        fotos_urls = []
        fecha_actualizacion = None
        tiene_reconocimiento = False
        
        try:
            from seguridad.models import ReconocimientoFacial, Copropietarios
            
            # Buscar por copropietario asociado al usuario
            copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
            
            if copropietario:
                reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
                
                if reconocimiento:
                    # 🔧 CORRECCIÓN CRÍTICA: Los datos están en vector_facial
                    if reconocimiento.vector_facial:
                        try:
                            fotos_urls = json.loads(reconocimiento.vector_facial)
                            tiene_reconocimiento = len(fotos_urls) > 0
                            fecha_actualizacion = reconocimiento.fecha_modificacion
                        except (json.JSONDecodeError, TypeError):
                            fotos_urls = []
                    
                    # Fallback: imagen_referencia_url
                    if not fotos_urls and reconocimiento.imagen_referencia_url:
                        fotos_urls = [reconocimiento.imagen_referencia_url]
                        tiene_reconocimiento = True
                        fecha_actualizacion = reconocimiento.fecha_modificacion
            
        except Exception:
            pass
        
        # 3. Respuesta exitosa
        return Response({
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
        }, status=status.HTTP_200_OK)
        
    except Usuario.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
'''
    
    print("\n4. 📝 CÓDIGO CORREGIDO GENERADO:")
    print("   - Archivo: authz/views_fotos_reconocimiento_corregido.py")
    print("   - Función: obtener_fotos_reconocimiento_corregido")
    print("   - Corrección: Lee directamente de vector_facial")
    
    return codigo_corregido

if __name__ == "__main__":
    # Ejecutar corrección
    fotos_encontradas = corregir_endpoint_get_fotos()
    codigo_nuevo = generar_version_corregida()
    
    print(f"\n🎯 RESULTADO: {len(fotos_encontradas)} fotos encontradas")
    print("\n✅ PRÓXIMO PASO: Aplicar la corrección al archivo")