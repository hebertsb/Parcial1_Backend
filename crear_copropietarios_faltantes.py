import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from seguridad.models import Copropietarios

def crear_copropietarios_faltantes():
    """🔧 Crear copropietarios para usuarios propietarios que no los tienen"""
    print("=" * 70)
    print("🔧 CREAR COPROPIETARIOS FALTANTES")
    print("=" * 70)
    
    rol_propietario = Rol.objects.filter(nombre='Propietario').first()
    if not rol_propietario:
        print("❌ No existe rol 'Propietario'")
        return
    
    usuarios_propietarios = Usuario.objects.filter(roles=rol_propietario)
    creados = 0
    
    for usuario in usuarios_propietarios:
        try:
            # Verificar si ya tiene copropietario
            Copropietarios.objects.get(usuario_sistema=usuario)
            print(f"✅ {usuario.email} ya tiene copropietario")
        except Copropietarios.DoesNotExist:
            # Crear copropietario automáticamente
            try:
                copropietario = Copropietarios.objects.create(
                    nombres=usuario.persona.nombre if usuario.persona else "Propietario",
                    apellidos=usuario.persona.apellido if usuario.persona else "Sistema",
                    numero_documento=usuario.persona.documento_identidad if usuario.persona else f"DOC{usuario.id}",
                    email=usuario.email,
                    telefono=usuario.persona.telefono if (usuario.persona and usuario.persona.telefono) else "000000000",
                    unidad_residencial=f"Unidad {usuario.id}",  # Por defecto
                    tipo_residente='Propietario',
                    usuario_sistema=usuario,
                    activo=True
                )
                print(f"🆕 Creado copropietario para {usuario.email} (ID: {copropietario.id})")
                creados += 1
            except Exception as e:
                print(f"❌ Error creando copropietario para {usuario.email}: {e}")
    
    print(f"\n✅ Copropietarios creados: {creados}")
    print("Ahora todos los usuarios propietarios pueden usar reconocimiento facial")

if __name__ == '__main__':
    crear_copropietarios_faltantes()