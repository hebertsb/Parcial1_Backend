import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol
from seguridad.models import Copropietarios, ReconocimientoFacial

def explicar_relaciones_completas():
    """📋 Explicar cómo funcionan las relaciones del sistema"""
    print("=" * 80)
    print("📋 EXPLICACIÓN COMPLETA: RELACIONES DEL SISTEMA")
    print("=" * 80)
    
    # 1. Verificar Usuario con rol Propietario
    usuario = Usuario.objects.get(id=8)
    print(f"🧑 USUARIO:")
    print(f"   - ID: {usuario.id}")
    print(f"   - Email: {usuario.email}")
    print(f"   - Persona ID: {usuario.persona.id}")
    print(f"   - Nombre: {usuario.persona.nombre} {usuario.persona.apellido}")
    
    # Verificar roles
    roles = usuario.roles.all()
    print(f"   - Roles: {[r.nombre for r in roles]}")
    
    # 2. Verificar si tiene entrada en Copropietarios
    try:
        copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
        print(f"\n🏠 COPROPIETARIO (seguridad.models):")
        print(f"   - ID: {copropietario.id}")
        print(f"   - Nombres: {copropietario.nombres}")
        print(f"   - Apellidos: {copropietario.apellidos}")
        print(f"   - Email: {copropietario.email}")
        print(f"   - Unidad: {copropietario.unidad_residencial}")
        print(f"   - Tipo residente: {copropietario.tipo_residente}")
        print(f"   - Usuario sistema: {copropietario.usuario_sistema.email if copropietario.usuario_sistema else 'None'}")
        
        # 3. Verificar ReconocimientoFacial
        try:
            reconocimiento = ReconocimientoFacial.objects.get(copropietario_id=copropietario.id)
            print(f"\n📷 RECONOCIMIENTO FACIAL:")
            print(f"   - ID: {reconocimiento.id}")
            print(f"   - Copropietario ID: {reconocimiento.copropietario_id}")
            print(f"   - Activo: {reconocimiento.activo}")
            print(f"   - Proveedor IA: {reconocimiento.proveedor_ia}")
            
            # Verificar fotos
            import json
            fotos_count = 0
            if hasattr(reconocimiento, 'fotos_urls') and reconocimiento.fotos_urls:
                try:
                    fotos = json.loads(reconocimiento.fotos_urls)
                    fotos_count = len(fotos)
                    print(f"   - Fotos en fotos_urls: {fotos_count}")
                except:
                    pass
            
            if fotos_count == 0 and reconocimiento.vector_facial:
                try:
                    fotos = json.loads(reconocimiento.vector_facial)
                    fotos_count = len(fotos)
                    print(f"   - Fotos en vector_facial: {fotos_count}")
                except:
                    pass
            
        except ReconocimientoFacial.DoesNotExist:
            print(f"\n❌ NO HAY RECONOCIMIENTO FACIAL para copropietario {copropietario.id}")
            
    except Copropietarios.DoesNotExist:
        print(f"\n❌ NO HAY ENTRADA EN COPROPIETARIOS para usuario {usuario.id}")
        print("   Esto significa que el usuario tiene rol 'Propietario' pero")
        print("   no tiene registro en la tabla 'seguridad.Copropietarios'")
    
    print(f"\n" + "=" * 80)
    print("🧩 EXPLICACIÓN DEL FLUJO:")
    print("=" * 80)
    print("1. USUARIO (authz.models.Usuario)")
    print("   - Tiene rol 'Propietario' asignado")
    print("   - Es la entidad principal de autenticación")
    print()
    print("2. COPROPIETARIO (seguridad.models.Copropietarios)")
    print("   - Es un 'perfil adicional' para usuarios del condominio")
    print("   - Almacena info específica: unidad_residencial, tipo_residente")
    print("   - Campo 'usuario_sistema' apunta al Usuario")
    print("   - ¡IMPORTANTE! No todos los usuarios tienen copropietario")
    print()
    print("3. RECONOCIMIENTO FACIAL (seguridad.models.ReconocimientoFacial)")
    print("   - Almacena las fotos y datos biométricos")
    print("   - Campo 'copropietario_id' apunta al Copropietario")
    print("   - ¡NO apunta directamente al Usuario!")
    print()
    print("🔗 CADENA DE RELACIÓN:")
    print("   Usuario → Copropietario → ReconocimientoFacial")
    print("   (authz)     (seguridad)      (seguridad)")

def mostrar_todos_copropietarios():
    """📊 Mostrar todos los copropietarios y sus usuarios"""
    print(f"\n" + "=" * 80)
    print("📊 TODOS LOS COPROPIETARIOS EN EL SISTEMA:")
    print("=" * 80)
    
    copropietarios = Copropietarios.objects.all()
    print(f"Total copropietarios: {copropietarios.count()}")
    
    for cop in copropietarios:
        usuario_email = cop.usuario_sistema.email if cop.usuario_sistema else "SIN USUARIO"
        print(f"ID {cop.id}: {cop.nombres} {cop.apellidos} → {usuario_email}")
        
        # Verificar si tiene reconocimiento facial
        reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=cop.id).first()
        if reconocimiento:
            print(f"   ✅ Tiene reconocimiento facial (ID: {reconocimiento.id})")
        else:
            print(f"   ❌ Sin reconocimiento facial")

def mostrar_usuarios_propietarios_sin_copropietario():
    """⚠️ Mostrar usuarios con rol Propietario que NO tienen copropietario"""
    print(f"\n" + "=" * 80)
    print("⚠️ USUARIOS PROPIETARIOS SIN COPROPIETARIO:")
    print("=" * 80)
    
    rol_propietario = Rol.objects.filter(nombre='Propietario').first()
    if rol_propietario:
        usuarios_propietarios = Usuario.objects.filter(roles=rol_propietario)
        print(f"Total usuarios con rol Propietario: {usuarios_propietarios.count()}")
        
        sin_copropietario = []
        for usuario in usuarios_propietarios:
            try:
                Copropietarios.objects.get(usuario_sistema=usuario)
                print(f"✅ {usuario.email} → TIENE copropietario")
            except Copropietarios.DoesNotExist:
                sin_copropietario.append(usuario)
                print(f"❌ {usuario.email} → SIN copropietario")
        
        if sin_copropietario:
            print(f"\n⚠️ {len(sin_copropietario)} usuarios propietarios necesitan copropietario")
            print("   Para que puedan usar reconocimiento facial")

def main():
    """🚀 Explicación completa"""
    print("🎯 ENTENDIENDO LAS RELACIONES DEL SISTEMA")
    
    explicar_relaciones_completas()
    mostrar_todos_copropietarios()
    mostrar_usuarios_propietarios_sin_copropietario()
    
    print(f"\n" + "=" * 80)
    print("💡 CONCLUSIÓN:")
    print("=" * 80)
    print("El sistema usa DOS tablas separadas:")
    print("1. authz.Usuario (autenticación + roles)")
    print("2. seguridad.Copropietarios (perfil de residente)")
    print()
    print("Para reconocimiento facial necesitas AMBAS:")
    print("- Usuario con rol 'Propietario'")
    print("- Entrada en Copropietarios con usuario_sistema apuntando al Usuario")
    print("- ReconocimientoFacial con copropietario_id apuntando al Copropietario")
    print()
    print("Es como tener:")
    print("- Una cuenta de usuario (login/password/roles)")
    print("- Un perfil de residente (unidad, tipo, datos específicos)")
    print("- Datos biométricos (fotos, vectores faciales)")

if __name__ == '__main__':
    main()