import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario, Rol, SolicitudRegistroPropietario
from seguridad.models import Copropietarios

def verificar_proceso_completo():
    """🔍 Verificar el proceso completo de registro"""
    print("=" * 80)
    print("🔍 VERIFICANDO PROCESO DE REGISTRO DE PROPIETARIOS")
    print("=" * 80)
    
    # 1. Verificar el proceso actual de aprobación
    print("📋 PROCESO ACTUAL:")
    print("1. Usuario envía SolicitudRegistroPropietario")
    print("2. Admin aprueba → Se ejecuta solicitud.aprobar_solicitud()")
    print("3. Se crea Usuario con rol 'Propietario'")
    print("4. Usuario intenta subir fotos...")
    print("5. ❌ FALLA porque no hay Copropietario")
    
    # 2. Verificar solicitudes aprobadas recientes
    print(f"\n📊 SOLICITUDES APROBADAS:")
    solicitudes_aprobadas = SolicitudRegistroPropietario.objects.filter(estado='APROBADA')
    
    for solicitud in solicitudes_aprobadas[:5]:  # Últimas 5
        print(f"\n📄 Solicitud ID {solicitud.id}:")
        print(f"   - Email: {solicitud.email}")
        print(f"   - Estado: {solicitud.estado}")
        
        if hasattr(solicitud, 'usuario_creado') and solicitud.usuario_creado:
            usuario = solicitud.usuario_creado
            print(f"   - Usuario creado: ✅ ID {usuario.id}")
            
            # Verificar si tiene copropietario
            try:
                copropietario = Copropietarios.objects.get(usuario_sistema=usuario)
                print(f"   - Copropietario: ✅ ID {copropietario.id}")
            except Copropietarios.DoesNotExist:
                print(f"   - Copropietario: ❌ FALTA - No puede usar reconocimiento facial")
        else:
            print(f"   - Usuario creado: ❌ No tiene usuario asociado")

def mostrar_metodo_aprobar_solicitud():
    """📄 Mostrar cómo funciona el método aprobar_solicitud"""
    print(f"\n" + "=" * 80)
    print("📄 MÉTODO aprobar_solicitud() ACTUAL:")
    print("=" * 80)
    
    print("""
def aprobar_solicitud(self, revisado_por_usuario):
    # 1. Crear o buscar Persona
    persona, created = Persona.objects.get_or_create(...)
    
    # 2. Crear Usuario
    usuario = Usuario.objects.create_user(
        email=self.email,
        password=password_temporal,
        persona=persona
    )
    
    # 3. Asignar rol Propietario
    rol_propietario = Rol.objects.get_or_create(nombre='Propietario')
    usuario.roles.add(rol_propietario)
    
    # 4. ❌ NO CREA COPROPIETARIO AUTOMÁTICAMENTE
    # Aquí está el problema!
    
    return usuario, password_temporal
    """)
    
    print("🐛 PROBLEMA: El método NO crea entrada en Copropietarios")
    print("   Por eso los usuarios no pueden usar reconocimiento facial")

def proponer_solucion():
    """💡 Proponer solución al problema"""
    print(f"\n" + "=" * 80)
    print("💡 SOLUCIÓN PROPUESTA:")
    print("=" * 80)
    
    print("OPCIÓN 1: Modificar aprobar_solicitud() para crear Copropietario automáticamente")
    print("OPCIÓN 2: Crear middleware que auto-cree Copropietario cuando sea necesario")
    print("OPCIÓN 3: Modificar endpoint de reconocimiento para crear Copropietario si falta")
    
    print(f"\n🎯 RECOMENDACIÓN: OPCIÓN 1 (Más limpia)")
    print("Modificar el método aprobar_solicitud() para que:")
    print("1. Cree el Usuario")
    print("2. Cree el Copropietario automáticamente")
    print("3. Los vincule correctamente")
    
    print(f"\n📄 CÓDIGO PROPUESTO:")
    print("""
def aprobar_solicitud(self, revisado_por_usuario):
    # ... código existente ...
    
    # Crear Usuario
    usuario = Usuario.objects.create_user(...)
    usuario.roles.add(rol_propietario)
    
    # 🆕 AGREGAR: Crear Copropietario automáticamente
    copropietario = Copropietarios.objects.create(
        nombres=self.nombres,
        apellidos=self.apellidos,
        numero_documento=self.documento_identidad,
        email=self.email,
        telefono=self.telefono,
        unidad_residencial=self.numero_casa,  # o generar automáticamente
        tipo_residente='Propietario',
        usuario_sistema=usuario,
        activo=True
    )
    
    return usuario, password_temporal
    """)

def main():
    """🚀 Verificación completa"""
    print("🎯 ANÁLISIS: PROBLEMA EN PROCESO DE REGISTRO")
    
    verificar_proceso_completo()
    mostrar_metodo_aprobar_solicitud()
    proponer_solucion()
    
    print(f"\n" + "=" * 80)
    print("🎯 CONCLUSIÓN:")
    print("=" * 80)
    print("✅ Has identificado correctamente el problema")
    print("❌ Usuarios aprobados NO pueden usar reconocimiento facial")
    print("🔧 Necesitamos modificar aprobar_solicitud() para crear Copropietario")
    print("🎯 Esto hará que el proceso sea automático y transparente")

if __name__ == '__main__':
    main()