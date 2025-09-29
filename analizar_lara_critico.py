# 🔍 ANÁLISIS CRÍTICO: lara@gmail.com - FLUJO AUTOMÁTICO ROTO

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authz.models import Usuario
from seguridad.models import Copropietarios, ReconocimientoFacial

def analizar_usuario_lara():
    """
    🎯 Verificar el estado completo de lara@gmail.com
    """
    print('🔍 ANÁLISIS CRÍTICO: lara@gmail.com')
    print('=' * 45)
    
    try:
        # 1. Verificar usuario
        usuario = Usuario.objects.get(email='lara@gmail.com')
        print(f'✅ Usuario ID: {usuario.id}')
        print(f'   - Email: {usuario.email}')
        persona_nombre = usuario.persona.nombre if usuario.persona else 'Sin persona'
        print(f'   - Nombre: {persona_nombre}')
        print(f'   - Roles: {[r.nombre for r in usuario.roles.all()]}')
        
        # 2. Verificar copropietario
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        if copropietario:
            print(f'✅ Copropietario ID: {copropietario.id}')
            print(f'   - Nombres: {copropietario.nombres} {copropietario.apellidos}')
            print(f'   - Casa: {copropietario.unidad_residencial}')
            print(f'   - Activo: {copropietario.activo}')
            
            # 3. Verificar reconocimiento facial
            reconocimiento = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).first()
            if reconocimiento:
                print(f'✅ ReconocimientoFacial ID: {reconocimiento.id}')
                print(f'   - Activo: {reconocimiento.activo}')
                vector_len = len(str(reconocimiento.vector_facial)) if reconocimiento.vector_facial else 0
                print(f'   - Vector facial: {vector_len} caracteres')
            else:
                print('❌ NO TIENE ReconocimientoFacial')
                print('   🔧 CRÍTICO: Falta registro de reconocimiento facial')
        else:
            print('❌ NO TIENE Copropietario')
            print('   🔧 CRÍTICO: El flujo automático falló completamente')
        
        # 4. DIAGNÓSTICO FINAL
        print(f'\n📊 DIAGNÓSTICO FINAL:')
        print(f'   Usuario: ✅ OK')
        print(f'   Copropietario: {"✅ OK" if copropietario else "❌ FALTA"}')
        
        if copropietario:
            reconoc_ok = ReconocimientoFacial.objects.filter(copropietario_id=copropietario.id).exists()
            print(f'   ReconocimientoFacial: {"✅ OK" if reconoc_ok else "❌ FALTA"}')
            
            if not reconoc_ok:
                print(f'\n🔧 CORRECCIÓN INMEDIATA REQUERIDA:')
                print(f'   - Copropietario ID: {copropietario.id}')
                print(f'   - SQL: INSERT INTO reconocimiento_facial (copropietario_id, ...) VALUES ({copropietario.id}, ...)')
                return {'copropietario_id': copropietario.id, 'necesita_reconocimiento': True}
            else:
                print(f'\n✅ USUARIO COMPLETAMENTE CONFIGURADO')
                return {'copropietario_id': copropietario.id, 'necesita_reconocimiento': False}
        else:
            print(f'   ReconocimientoFacial: ❌ FALTA (depende de Copropietario)')
            print(f'\n🚨 FLUJO AUTOMÁTICO COMPLETAMENTE ROTO')
            print(f'   - AMBOS registros faltan: Copropietario + ReconocimientoFacial')
            return {'usuario_id': usuario.id, 'necesita_ambos': True}
            
    except Usuario.DoesNotExist:
        print('❌ Usuario lara@gmail.com NO ENCONTRADO')
        print('   - Verificar si el usuario fue creado correctamente')
        return {'error': 'usuario_no_encontrado'}
    except Exception as e:
        print(f'❌ Error inesperado: {e}')
        return {'error': str(e)}

def verificar_flujo_automatico():
    """
    🔍 Verificar si el flujo automático está realmente roto
    """
    print(f'\n🔍 VERIFICAR FLUJO AUTOMÁTICO GLOBAL')
    print('=' * 40)
    
    # Buscar usuarios recientes sin copropietario
    usuarios_sin_copropietario = []
    usuarios_recientes = Usuario.objects.filter(roles__nombre='Propietario').order_by('-id')[:10]
    
    for usuario in usuarios_recientes:
        copropietario = Copropietarios.objects.filter(usuario_sistema=usuario).first()
        if not copropietario:
            usuarios_sin_copropietario.append(usuario)
    
    print(f'📊 USUARIOS PROPIETARIOS RECIENTES: {len(usuarios_recientes)}')
    print(f'❌ SIN COPROPIETARIO: {len(usuarios_sin_copropietario)}')
    
    if usuarios_sin_copropietario:
        print(f'\n🚨 USUARIOS AFECTADOS POR FLUJO ROTO:')
        for usuario in usuarios_sin_copropietario:
            print(f'   - ID {usuario.id}: {usuario.email}')
        
        return True  # Flujo roto
    else:
        print(f'✅ Todos los usuarios propietarios tienen copropietario')
        return False  # Flujo OK

if __name__ == "__main__":
    # Análisis principal
    resultado = analizar_usuario_lara()
    flujo_roto = verificar_flujo_automatico()
    
    print(f'\n🎯 CONCLUSIONES:')
    if flujo_roto:
        print('🚨 FLUJO AUTOMÁTICO CONFIRMADO COMO ROTO')
        print('⚡ ACCIÓN REQUERIDA: Corregir método aprobar_solicitud')
    else:
        print('✅ Flujo automático funciona para otros usuarios')
        print('🔧 Problema específico de lara@gmail.com')