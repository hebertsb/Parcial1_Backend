# 🔧 CORRECCIÓN INMEDIATA: lara@gmail.com - Crear ReconocimientoFacial

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from seguridad.models import Copropietarios, ReconocimientoFacial
from django.utils import timezone

def crear_reconocimiento_lara():
    """
    🎯 Crear registro ReconocimientoFacial para lara@gmail.com
    """
    print('🔧 CORRECCIÓN INMEDIATA: lara@gmail.com')
    print('=' * 45)
    
    try:
        # 1. Obtener copropietario de lara
        copropietario = Copropietarios.objects.get(id=12)
        print(f'✅ Copropietario encontrado: {copropietario.nombres} {copropietario.apellidos}')
        print(f'   - ID: {copropietario.id}')
        print(f'   - Casa: {copropietario.unidad_residencial}')
        
        # 2. Verificar si ya existe ReconocimientoFacial
        reconocimiento_existente = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        if reconocimiento_existente:
            print(f'⚠️  Ya existe ReconocimientoFacial ID: {reconocimiento_existente.id}')
            return False
        
        # 3. Crear ReconocimientoFacial con TODOS los campos requeridos
        reconocimiento = ReconocimientoFacial.objects.create(
            copropietario=copropietario,
            proveedor_ia='Local',
            vector_facial='[]',  # Array vacío para empezar (obligatorio)
            activo=True,
            fecha_enrolamiento=timezone.now(),
            fecha_modificacion=timezone.now(),
            intentos_verificacion=0
        )
        
        print(f'✅ ReconocimientoFacial creado exitosamente')
        print(f'   - ID: {reconocimiento.id}')
        print(f'   - Copropietario: {reconocimiento.copropietario.nombres} {reconocimiento.copropietario.apellidos}')
        print(f'   - Activo: {reconocimiento.activo}')
        print(f'   - Fecha enrolamiento: {reconocimiento.fecha_enrolamiento}')
        
        return True
        
    except Copropietarios.DoesNotExist:
        print('❌ Copropietario ID 12 no encontrado')
        return False
    except Exception as e:
        print(f'❌ Error creando ReconocimientoFacial: {e}')
        return False

def verificar_correccion():
    """
    ✅ Verificar que la corrección funcionó
    """
    print(f'\n✅ VERIFICACIÓN POST-CORRECCIÓN')
    print('=' * 35)
    
    try:
        from authz.models import Usuario
        
        # Verificar usuario lara
        usuario = Usuario.objects.get(email='lara@gmail.com')
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
        
        print(f'Usuario ID: {usuario.id} - {usuario.email}')
        print(f'Copropietario ID: {copropietario.id} - {"✅" if copropietario else "❌"}')
        print(f'ReconocimientoFacial ID: {reconocimiento.id if reconocimiento else "❌"} - {"✅" if reconocimiento else "❌"}')
        
        if usuario and copropietario and reconocimiento:
            print(f'\n🎉 ¡LARA CORREGIDA EXITOSAMENTE!')
            print(f'   - Ahora puede subir fotos de reconocimiento facial')
            print(f'   - Aparecerá en el panel de seguridad')
            return True
        else:
            print(f'\n❌ Corrección incompleta')
            return False
            
    except Exception as e:
        print(f'❌ Error en verificación: {e}')
        return False

if __name__ == "__main__":
    # Ejecutar corrección
    print('🚀 INICIANDO CORRECCIÓN TEMPORAL PARA lara@gmail.com')
    print('=' * 55)
    
    exito = crear_reconocimiento_lara()
    
    if exito:
        verificar_correccion()
        print(f'\n🎯 PRÓXIMO PASO: Corregir flujo automático para futuros usuarios')
    else:
        print(f'\n❌ La corrección falló')